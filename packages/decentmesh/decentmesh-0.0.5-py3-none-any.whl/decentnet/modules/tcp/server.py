import asyncio
import logging
import multiprocessing
import socket
from threading import Thread

import rich
from rich.panel import Panel

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.consensus.difficulty_ports_mapping import PORT_DIFFICULTY_CONFIG
from decentnet.modules.comm.relay import Relay
from decentnet.modules.logger.log import setup_logger
from decentnet.modules.tasks_base.consumer import Consumer
from decentnet.modules.tasks_base.r2r_comm import R2RComm
from decentnet.modules.tcp.db_functions import remove_alive_beam_from_db_w_pub_key

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG)


class TCPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.clients = []

    @staticmethod
    def create_socket(host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return sock

    @staticmethod
    def handle_client(client_socket,
                      beam_pipe_comm: dict):
        """
        Handle a client connection

        ! This function is run by separate process
        :param client_socket:
        :param beam_pipe_comm:
        :return:
        """

        relay = Relay(client_socket, beam_pipe_comm)
        try:
            sock_name = client_socket.getsockname()
        except OSError as e:
            logger.error(e)
            logger.info("Socket was closed, unable to continue.")
            return

        Thread(target=lambda: R2RComm(relay), name=f"R2R Communication {relay.target_key}",
               daemon=True).start()
        Thread(target=lambda: Consumer(relay),
               name=f"Consumer {sock_name}", daemon=True).start()

        while True:
            if not relay.do_relaying():
                logger.debug(f"Received 0 data from :{relay.local_port}")
                logger.info(
                    f"Disconnected {sock_name[0]}:{relay.local_port}")  # TODO: Delete from connected
                asyncio.run(relay.disconnect_beacon(relay.local_port, relay.beam_pub_key))
                asyncio.run(remove_alive_beam_from_db_w_pub_key(relay.beam_pub_key))
                break

    def run(self):
        diff_setting = PORT_DIFFICULTY_CONFIG[self.port]
        self.server.listen(diff_setting.max_hosts)
        logger.info(f"[*] Listening on {self.host}:{self.port}")
        welcome_string = (f"Started DecentMesh... OK\n"
                          f"Listening on {self.host}:{self.port}\n"
                          f"Listening for maximum hosts {diff_setting.max_hosts}\n"
                          f"Seed difficulty: {diff_setting.seed_difficulty}\n"
                          f"Low difficulty: {diff_setting.low_diff}")
        rich.print(Panel(welcome_string, title="DecentMesh Status"))
        manager = multiprocessing.Manager()
        beam_pipe_comm = manager.dict()

        while True:
            client_socket, client_address = self.server.accept()

            logger.info(
                f"[*] Accepted connection from {client_address[0]}:{client_address[1]}")
            client_process = multiprocessing.Process(target=TCPServer.handle_client,
                                                     name=f"Handling client {client_address}",
                                                     args=(
                                                         client_socket, beam_pipe_comm))
            client_process.start()

    def close(self):
        for client_socket in self.clients:
            client_socket.close()
        self.server.close()
