# pqct/toolkit.py

from .algorithms import LatticeBasedKyber, LatticeBasedDilithium

class PostQuantumCryptoToolkit:
    def __init__(self):
        self.supported_algorithms = {
            'kyber': LatticeBasedKyber(),
            'dilithium': LatticeBasedDilithium()
        }

    def encrypt(self, algorithm, plaintext):
        alg = self.supported_algorithms.get(algorithm.lower())
        if alg is None:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        public_key, _ = alg.generate_keypair()
        return alg.encrypt(public_key, plaintext)

    def decrypt(self, algorithm, ciphertext, secret_key):
        alg = self.supported_algorithms.get(algorithm.lower())
        if alg is None:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        return alg.decrypt(secret_key, ciphertext)

    def sign(self, algorithm, message):
        alg = self.supported_algorithms.get(algorithm.lower())
        if alg is None:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        _, secret_key = alg.generate_keypair()
        return alg.sign(secret_key, message)

    def verify(self, algorithm, message, signature, public_key):
        alg = self.supported_algorithms.get(algorithm.lower())
        if alg is None:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        return alg.verify(public_key, message, signature)
