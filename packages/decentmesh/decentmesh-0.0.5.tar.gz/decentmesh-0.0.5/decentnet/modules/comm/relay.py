import asyncio
import datetime
import logging
from multiprocessing import Pipe
from threading import Thread
from typing import Callable, Coroutine, Any

import cbor2
import networkx as nx
import sqlalchemy
from networkx import NodeNotFound, NetworkXNoPath
from prometheus_client import Gauge
from sqlalchemy.exc import IntegrityError

from decentnet.consensus.cmd_enum import CMD
from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.consensus.local_config import registry
from decentnet.consensus.routing_params import MAX_ROUTE_LENGTH, DEFAULT_CAPACITY
from decentnet.modules.blockchain.block import Block
from decentnet.modules.comm.beam import Beam
from decentnet.modules.cryptography.asymetric import AsymCrypt
from decentnet.modules.db.base import session_scope
from decentnet.modules.db.models import NodeInfoTable, AliveBeam
from decentnet.modules.forwarding.flow_net import FlowNetwork
from decentnet.modules.internal_processing.blocks import ProcessingBlock
from decentnet.modules.key_util.key_manager import KeyManager
from decentnet.modules.logger.log import setup_logger
from decentnet.modules.serializer.serializer import Serializer
from decentnet.modules.tasks_base.publisher import RedisPublisher
from decentnet.modules.tcp.socket_functions import recv_all
from decentnet.modules.timer.timer import Timer
from decentnet.modules.transfer.packager import Packager

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG)

prom_block_process_time = Gauge('block_process_time', 'Time spent processing a block',
                                registry=registry)
prom_data_received = Gauge("data_received_for_relay", "Data received for relaying",
                           registry=registry)
prom_path_length = Gauge("path_length", "Path length for relaying data",
                         registry=registry)
prom_data_published = Gauge("data_published_for_relay", "Data published for relaying",
                            registry=registry)

AsyncCallbackType = Callable[[str, str], Coroutine[Any, Any, Any]]


class Relay:

    def __init__(self, client_socket, beam_pipe_comm: dict, callback: AsyncCallbackType | None = None,
                 beam: Beam | None = None):
        """
        Creates a passive relay that will listen on socket and relay incoming beams
        :param client_socket:
        :param callback:
        """
        self.alive = True
        self.beam_pipe_comm = beam_pipe_comm
        self.beam_pub_key = None
        self.socket = client_socket
        self.client_ip = client_socket.getpeername()
        self.__callback = callback

        logger.debug(f"Initial Connection {self.client_ip}")
        self.local_port = self.client_ip[
            1]  # This needs to be set as after disconnect information about previous port dispersal

        logger.info("Waiting for genesis block from new sender...")
        request = recv_all(self.socket, self.client_ip[0], self.local_port)
        if not request:
            return

        self.network = FlowNetwork()
        self.publisher = RedisPublisher()

        verified, unpacked_request, verified_csig = Packager.unpack(request)

        Packager.check_verified(unpacked_request, verified)

        if verified_csig is not None:
            self.execute_network_cmd(unpacked_request, verified_csig)
            return

        block = Block.from_bytes(
            unpacked_request["data"])  # Difficulty is checked when adding to blockchain

        self.beam_pub_key = pub_key = unpacked_request[
            "pub"]  # Key, which is received from unknown entity
        self.target_key = target_key = unpacked_request[
            "target"]  # Key of mine or next destination

        self.public_key_id = 1  # Make this rotated
        self.public_key_enc_id = 4

        _, self.relay_pub_key = KeyManager.retrieve_ssh_key_pair_from_db(self.public_key_id)

        # Save key of a client
        if not beam:
            # Create a pipe for a relay beam communication between processes
            beam_pipe_comm[pub_key] = Pipe()

            self.beam = Beam(self.public_key_id, self.public_key_enc_id, target_key)
            self.beam.connect_using_socket(client_socket)
            self.beam.initialize_incoming_transmission(block)
        else:
            self.beam = beam

        self.beam.lock()

        if target_key != "NOT_KNOWN":
            self.relay_message_by_one(block, unpacked_request, request)

        _, o_pub_key = KeyManager.retrieve_ssh_key_pair_from_db(self.public_key_id)
        signing_pub_key = AsymCrypt.verifying_key_to_string(o_pub_key)

        self.network.add_edge(signing_pub_key,
                              pub_key, DEFAULT_CAPACITY)
        self.network.add_edge(target_key, pub_key, DEFAULT_CAPACITY)

        if block.index == 0:
            logger.info(f"Adding connected Beacon {pub_key}")
            asyncio.run(self.save_beacon(pub_key))
            # TODO: transmit connection to other connected beacons and relays
            Thread(
                target=lambda: self.broadcast_connected(block, pub_key, unpacked_request), daemon=True,
                name=f"Broadcasting of {pub_key}").start()
        else:
            logger.info(f"Updating beacon connection {pub_key}")
            asyncio.run(self.update_beacon_connection(pub_key))
            self.network.add_edge(pub_key,
                                  KeyManager.key_to_base64(target_key), None)

        if not self.beam.alive:
            self.beam.close()
            logger.warning("INVALID BLOCK, Closed connection")
        else:
            asyncio.run(self.beam.save_new_pub_key(pub_key, False, "New Beacon"))

        # New Difficulty is sending in the genesis block
        # new_diff = BlockchainParams.low_diff
        # Send new difficulty of blockchain
        # self.beam.send_new_difficulty(new_diff)

    def broadcast_connected(self, genesis_block: Block, connected_pub_key: str,
                            unpacked_genesis: dict):
        """

        :param genesis_block:
        :param connected_pub_key: Pub key of the connected beacon needs to be base64
        :param unpacked_genesis:
        """
        if genesis_block.index == 0:
            # Broadcast newly connected to all beams
            with session_scope() as session:
                all_alive_beams = session.query(AliveBeam).where(AliveBeam.ready).all()
                if len(all_alive_beams):
                    logger.info(
                        f"Broadcasting connected beacon {connected_pub_key} to connected beams")
                    _data = Packager.add_cmd(unpacked_genesis,
                                             self.public_key_id,
                                             CMD.BROADCAST.value)

                    block_with_signature = {"data": _data["data"], "sig": _data["sig"], "pub": _data["pub"]}

                    # Template next connection block with broadcast block
                    broadcast_block = self.beam.conn_bc.template_next_block(
                        self.beam.conn_bc.difficulty,
                        cbor2.dumps(block_with_signature))
                    if not self.beam.conn_bc.insert(broadcast_block):
                        raise Exception("Failed to insert broadcast block")

                    broadcast_block_bytes = broadcast_block.to_bytes()

                    broadcast_block_signature = Packager.sign_block(self.public_key_id,
                                                                    broadcast_block_bytes)

                    serialized_broadcast = Serializer.serialize_data(self.relay_pub_key,
                                                                     broadcast_block_signature,
                                                                     broadcast_block_bytes,
                                                                     _data["target"],
                                                                     _data["cmd"],
                                                                     _data["csig"],
                                                                     _data["cpub"])
                else:
                    logger.info(f"No one to broadcast to {connected_pub_key}")
                    return

                for beam in all_alive_beams:
                    if beam.pub_key != connected_pub_key:
                        logger.info(f"  broadcasting connection to {beam.pub_key}")
                        self.publisher.publish_message(beam.pub_key,
                                                       serialized_broadcast)

                # if target_pub_key == "NOT_KNOWN":
                #    return
                # TODO: make it efficient
                # target_connected = None
                # tries = 0
                # while not target_connected and tries < 30:
                #    logger.debug(f"Waiting for target to connect {tries}/30")
                #    target_connected = session.query(AliveBeam).where(
                #        AliveBeam.pub_key == target_pub_key and AliveBeam.ready).first()
                #    tries += 1
                #    sleep(5)
                # if target_connected:
                #    self.publisher.publish_message(target_pub_key, serialized_broadcast)
                # else:
                #    logger.warning(f"Waiting for target {target_pub_key} timed out.")

    async def update_beacon_connection(self, pub_key):
        await Relay.update_beacon(pub_key)
        await self.do_callback(pub_key, "ping")

    async def do_callback(self, pub_key: str, action: str):
        if self.__callback:
            await self.__callback(pub_key, action)

    def do_relaying(self):
        self.alive = True
        logger.debug(
            f"Waiting for data from {self.beam_pub_key} for relaying on {self.client_ip}...")
        request = recv_all(self.socket, self.client_ip[0], self.local_port)

        if not request:
            self.alive = False
            return 0

        request_size = len(request)
        prom_data_received.set(request_size)
        logger.info(f"Relay Connection {self.socket.getpeername()}")
        try:
            self.relay_request(request)
        except (cbor2.CBORDecodeError, cbor2.CBORDecodeValueError):
            logger.error(f"Unable to decode: {request}")
            logger.error("Suggesting disconnect")
            self.beam.unlock()
            self.alive = False
            return 0

        return request_size

    async def _execute_network_cmd(self, data: dict, cmd_value: int):
        await self.do_callback(data["pub"], CMD(cmd_value).name)
        if cmd_value == CMD.BROADCAST.value:
            ProcessingBlock.proces_broadcast_block(self.network, data)
        if cmd_value == CMD.SYNCHRONIZE.value:
            block = Block.from_bytes(
                data["data"])
            self.beam.comm_bc.insert(block)

    def relay_request(self, request):
        t = Timer()

        verified, data, verified_csig = Packager.unpack(request)

        logger.debug(f"Unpacking took {t.stop()} ms")
        Packager.check_verified(data, verified)

        if verified_csig is not None:
            self.execute_network_cmd(data, verified_csig)
            return

        # This takes some time as the block hash needs to be computed
        block = Block.from_bytes(data["data"])  # TODO: Check difficulty
        logger.debug(f"Block from bytes took {t.stop()} ms")

        block.signature = data["sig"]
        beacon_pub_key = data["pub"]

        self.beam.comm_bc.difficulty = block.diff
        insert_res = self.beam.comm_bc.insert(block)

        asyncio.run(self.update_beacon_connection(beacon_pub_key))

        if not insert_res:
            logger.error(
                f"Failed to insert block, closing connection... {self.client_ip}")
            self.socket.close()
            self.alive = False

        block_process_time_timer = t.stop()
        logger.debug(f"New block processed in {block_process_time_timer} ms")
        prom_block_process_time.set(block_process_time_timer)
        logger.debug(f"Running pathfinding for {data['target']} => {self.beam_pub_key}")
        if data["target"] == self.beam_pub_key:
            logger.debug("Block is delivered")
            # TODO: do actions

        elif block.index > 0:
            try:
                self.relay_message_by_one(block, data, request)
            except nx.NetworkXNoPath:
                logger.warning(
                    f"Currently no path found between {self.beam_pub_key} => {data['target']}")

    def execute_network_cmd(self, unpacked_request: dict, verified_csig: bool):
        Packager.check_verified(unpacked_request, verified_csig)
        cmd_value = unpacked_request["cmd"]
        logger.debug(f"Received verified cmd {CMD(cmd_value)}")
        asyncio.run(self._execute_network_cmd(unpacked_request, cmd_value))

    def relay_message_by_one(self, block, data, request):
        try:
            path, capacity = self.network.get_path(self.beam_pub_key,
                                                   data["target"])
        except NodeNotFound:
            logger.fatal(f"Node {data['target']} not found")
            self.socket.close()
            self.alive = False
            logger.debug(f"Socket closed. {self.client_ip}")
            return
        except NetworkXNoPath:
            logger.fatal(f"Path to {data['target']} not found")
            self.socket.close()
            self.alive = False
            logger.debug(f"Socket closed. {self.client_ip}")
            return

        logger.debug(
            f"Found path {path} and capacity {capacity} for block {block.index}")
        path_len = len(path)
        prom_path_length.set(path_len)
        if path and path_len > MAX_ROUTE_LENGTH:
            logger.info(
                "Maximum path exceeded, connecting to closer relay for better latency...")
            # TODO: connect to the closer relay to make shorter path
        # Relay message
        if len(path) == 1:
            logger.debug("Path too short")
            return

        request_len = len(request)
        logger.debug(
            f"Publishing from {self.beam_pub_key} message to {path[1]} block size {request_len} B")
        # TODO: save temporarily messages that can not be delivered
        prom_data_published.set(request_len)

        # TODO: send request to relay process of sender
        process_uid = path[1]
        if process_uid in self.beam_pipe_comm.keys():
            logger.debug(f"Sending {block} to PIPE {process_uid} from {self.beam_pub_key}")
            self.beam_pipe_comm[process_uid][1].send(block.to_bytes())
            # In case of race condition happening uncomment
            # Wait for ack to block from publish
            # res = self.beam_pipe_comm[process_uid][0].recv()
            # logger.debug(f"Received block insert status from PIPE {res}")
            # TODO: close pipe

        self.publisher.publish_message(path[1], request)

    @classmethod
    async def update_beacon(cls, pub_key: str):
        with session_scope() as session:
            beacon = session.query(NodeInfoTable).filter(
                NodeInfoTable.pub_key == pub_key).first()
            beacon.last_ping = datetime.datetime.now()
            session.commit()

    async def disconnect_beacon(self, port: int, pub_key: str):
        await self.do_callback(pub_key, "disconnect")
        with session_scope() as session:
            record_to_delete = session.query(NodeInfoTable).filter(
                NodeInfoTable.port == port and NodeInfoTable.pub_key == pub_key).first()
            if record_to_delete:
                session.delete(record_to_delete)
                session.commit()

    async def save_beacon(self, pub_key: str):
        await self.do_callback(pub_key, "connect")
        with session_scope() as session:
            client_ip = self.client_ip
            bdb = NodeInfoTable(ipv4=client_ip[0], port=client_ip[1],
                                pub_key=pub_key,
                                version=self.beam.conn_bc.version)

            session.add(bdb)
            try:
                session.commit()
            except (IntegrityError, sqlalchemy.exc.IntegrityError):
                logger.debug(f"Updating connected node {client_ip[0]}:{client_ip[1]}")
                session.rollback()
                await Relay.update_beacon(pub_key)
