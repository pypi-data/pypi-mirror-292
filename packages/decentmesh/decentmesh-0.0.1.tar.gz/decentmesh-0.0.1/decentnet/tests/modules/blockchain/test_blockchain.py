import random
import unittest

from decentnet.modules.blockchain.block import Block
from decentnet.modules.blockchain.blockchain import Blockchain
from decentnet.modules.pow.difficulty import Difficulty


class BlockchainTests(unittest.TestCase):
    def test_init(self):
        blockchain: Blockchain = Blockchain("some_msg")
        seed = blockchain.chain[0]
        print(f"Succeed {seed.compute_hash().value_as_hex()}")

    def test_insertion(self):
        blockchain: Blockchain = Blockchain("some_msg")
        seed = blockchain.chain[0]
        testdata = b"testssss"

        try:
            b = Block(1, seed.compute_hash().value, Difficulty(16, 8, 1, 8, 32), testdata)
            b.mine()
            self.assertTrue(blockchain.insert(b))
        except Exception as ex:
            self.fail(f"Thrown {ex}")
        self.assertEqual(len(blockchain.chain), 2)

    def test_insertion_long(self):
        blockchain: Blockchain = Blockchain("some_msg")

        for i in range(50):
            testdata = random.randbytes(8)
            try:
                b = Block(len(blockchain.chain),
                          blockchain.chain[-1].compute_hash().value,
                          Difficulty(16, 8, 1, random.randint(1, 8), 32), testdata)
                b.mine()
                print(f"Mined block {b} {b.ttc} ms")
                self.assertTrue(blockchain.insert(b))
            except Exception as ex:
                self.fail(f"Thrown {ex}")
        self.assertEqual(len(blockchain.chain), 51)


if __name__ == '__main__':
    unittest.main()
