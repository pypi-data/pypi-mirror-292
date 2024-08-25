import logging
import multiprocessing
import random
from time import sleep
from typing import Optional

from decentnet.consensus.dev_constants import RUN_IN_DEBUG, SEEDS_AGENT_LOG_LEVEL
from decentnet.consensus.net_constants import SEED_NODES_IPV4, SEED_NODES_IPV6
from decentnet.modules.comm.beacon import Beacon
from decentnet.modules.cryptography.asymetric import AsymCrypt
from decentnet.modules.forwarding.flow_net import FlowNetwork
from decentnet.modules.key_util.key_manager import KeyManager
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)
logger.setLevel(SEEDS_AGENT_LOG_LEVEL)

setup_logger(RUN_IN_DEBUG)


class SeedsAgent:

    def __init__(self, host: str, current_port: int):
        self.beams = []
        self.network = FlowNetwork()
        self.current_port = current_port
        self.host = host
        self.pub_key_enc_id = 4
        multiprocessing.Process(target=self.connect_to_seeds,
                                name="Seed connection agent").start()

    def connect_to_seeds(self, seeds_array: Optional[list] = None):
        if seeds_array:
            seed_nodes_copy = seeds_array
        else:
            seed_nodes_copy = SEED_NODES_IPV4 + SEED_NODES_IPV6

        for node_v4 in list(seed_nodes_copy):
            if node_v4[0] == self.host and node_v4[1] == self.current_port:
                # Skip current host to avoid loopback
                continue
            try:
                beacon = Beacon(node_v4[0], node_v4[1], 1)
                beam = beacon.create_beam("NOT_KNOWN", self.pub_key_enc_id)
                if beam is None or beam.client is None:
                    continue

                self.beams.append(beam)
                _, o_pub_key = KeyManager.retrieve_ssh_key_pair_from_db(
                    beam.pub_key_id)
                pub_key = AsymCrypt.verifying_key_to_string(o_pub_key)
                # Invalid target key
                self.network.add_edge(pub_key,
                                      beam.target_key, 10)
                # Thread(target=beam.wait, name=f"SEED_BEAM_{node_v4}",
                #       daemon=True).start()
                logger.info(f"[OK] Seed {node_v4[0]}:{node_v4[1]} connected!")
                seed_nodes_copy.remove(node_v4)
                # TODO: This should be at every beam
                # TODO: ask for genesis block so seed can use this beacon as a relay

            except (ConnectionError, ConnectionResetError, ConnectionRefusedError,
                    ConnectionAbortedError, TimeoutError):
                logger.debug(f"{node_v4[0]}:{node_v4[1]} failed to connect")
            finally:
                sleep(random.randint(1, 5))

        if len(seed_nodes_copy):
            logger.debug(
                f"Will run seed connecting for {len(seed_nodes_copy)} seeds again")
            sleep(10)
            self.connect_to_seeds(seed_nodes_copy)
