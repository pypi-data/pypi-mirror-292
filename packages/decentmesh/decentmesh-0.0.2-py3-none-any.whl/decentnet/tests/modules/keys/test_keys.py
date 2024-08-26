import unittest

from decentnet.modules.key_util.key_manager import KeyManager


class TestSSHKeyManager(unittest.TestCase):
    def setUp(self):
        self.key_manager = KeyManager()

    def test_generate_ssh_key_pair(self):
        private_key, public_key = self.key_manager.generate_singing_key_pair()
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)

    def test_save_and_retrieve_ssh_key_pair(self):
        private_key, public_key = self.key_manager.generate_singing_key_pair()
        _id = self.key_manager.save_to_db(private_key, public_key, "test",
                                          can_encrypt=False)

        retrieved_private_key, retrieved_public_key = self.key_manager.retrieve_ssh_key_pair_from_db(
            _id)
        self.assertEqual(private_key, retrieved_private_key)
        self.assertEqual(public_key, retrieved_public_key)
