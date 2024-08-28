import unittest

from decentnet.modules.comm.beam import Beam


class TestBeamHash(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # This method is called before tests in an individual class are run
        pass

    def test_create_beam_hash_length(self):
        # Test that the hash length is correct for blake2b (default is 64 characters long)
        beam_hash = Beam.create_beam_hash(21112)
        self.assertEqual(len(beam_hash), 128,
                         "The hash should be 128 characters long for the default blake2b.")

    def test_create_beam_hash_is_hex(self):
        # Test that the hash consists only of hexadecimal characters
        beam_hash = Beam.create_beam_hash(21112)
        hex_digits = set("0123456789abcdef")
        # Convert hash to a lower case to simplify checking
        self.assertTrue(all(c in hex_digits for c in beam_hash.lower()),
                        "The hash should be a hexadecimal string.")


if __name__ == '__main__':
    unittest.main()
