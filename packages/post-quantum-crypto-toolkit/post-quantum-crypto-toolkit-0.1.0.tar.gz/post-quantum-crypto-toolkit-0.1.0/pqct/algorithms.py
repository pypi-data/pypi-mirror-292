# pqct/algorithms.py

import numpy as np
from hashlib import sha3_256

class LatticeBasedKyber:
    def __init__(self, n=256, q=3329):
        self.n = n  # Dimension of the lattice
        self.q = q  # Modulus

    def generate_keypair(self):
        """Generate a public and private key pair."""
        s = np.random.randint(0, self.q, self.n)
        e = np.random.randint(0, self.q, self.n)
        A = np.random.randint(0, self.q, (self.n, self.n))
        b = (A @ s + e) % self.q
        public_key = (A, b)
        private_key = s
        return public_key, private_key

    def encrypt(self, public_key, plaintext):
        """Encrypt a message using the public key."""
        A, b = public_key
        r = np.random.randint(0, self.q, self.n)
        e1 = np.random.randint(0, self.q, self.n)
        e2 = np.random.randint(0, self.q, len(plaintext))
        
        u = (A.T @ r + e1) % self.q
        v = (b @ r + e2 + plaintext) % self.q
        return u, v

    def decrypt(self, private_key, ciphertext):
        """Decrypt a ciphertext using the private key."""
        u, v = ciphertext
        plaintext = (v - u @ private_key) % self.q
        return plaintext

class LatticeBasedDilithium:
    def __init__(self, n=256, q=3329):
        self.n = n  # Dimension of the lattice
        self.q = q  # Modulus

    def generate_keypair(self):
        """Generate a public and private key pair."""
        s = np.random.randint(0, self.q, self.n)
        A = np.random.randint(0, self.q, (self.n, self.n))
        t = A @ s % self.q
        public_key = (A, t)
        private_key = s
        return public_key, private_key

    def sign(self, private_key, message):
        """Sign a message using the private key."""
        z = np.random.randint(0, self.q, self.n)
        A = np.random.randint(0, self.q, (self.n, self.n))
        t = (A @ z + private_key @ message) % self.q
        signature = sha3_256(t).digest()
        return signature

    def verify(self, public_key, message, signature):
        """Verify a signature using the public key."""
        A, t = public_key
        challenge = (A @ message) % self.q
        expected_signature = sha3_256(challenge).digest()
        return expected_signature == signature
