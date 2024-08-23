# pqct/tests.py

import unittest
from .toolkit import PostQuantumCryptoToolkit
import numpy as np

class TestPostQuantumCryptoToolkit(unittest.TestCase):

    def setUp(self):
        self.toolkit = PostQuantumCryptoToolkit()
        self.plaintext = np.random.randint(0, 3329, 256)
        self.message = b"Test message"

    def test_kyber_encryption_decryption(self):
        public_key, private_key = self.toolkit.supported_algorithms['kyber'].generate_keypair()
        ciphertext = self.toolkit.encrypt('kyber', self.plaintext)
        decrypted = self.toolkit.decrypt('kyber', ciphertext, private_key)
        np.testing.assert_array_equal(decrypted, self.plaintext)

    def test_dilithium_sign_verify(self):
        public_key, private_key = self.toolkit.supported_algorithms['dilithium'].generate_keypair()
        signature = self.toolkit.sign('dilithium', self.message)
        verification = self.toolkit.verify('dilithium', self.message, signature, public_key)
        self.assertTrue(verification)

if __name__ == '__main__':
    unittest.main()
