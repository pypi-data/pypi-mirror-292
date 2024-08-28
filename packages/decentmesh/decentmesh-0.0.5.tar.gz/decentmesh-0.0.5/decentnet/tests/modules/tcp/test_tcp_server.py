import multiprocessing
import unittest

from decentnet.modules.blockchain.blockchain import Blockchain
from decentnet.modules.tcp.client import TCPClient
from decentnet.modules.tcp.server import TCPServer
from decentnet.modules.transfer.packager import Packager


class TestTCPCommunication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = TCPServer('127.0.0.1', 8886)
        cls.server_process = multiprocessing.Process(target=cls.server.run)
        cls.server_process.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.close()
        cls.server_process.terminate()

    def test_server_client_connect(self):
        client = TCPClient('127.0.0.1', 8886)
        bc = Blockchain("CONNECTED")

        data = Packager.pack(1,
                             bc.get_last(), None)
        response = client.send_message(data)

        self.assertEqual(response, "CONNECTED")

        client.close()


if __name__ == "__main__":
    unittest.main()
