```markdown
# pqct

**PQCT** is a Python toolkit for post-quantum cryptography, implementing lattice-based cryptographic algorithms inspired by Kyber and Dilithium. This toolkit provides a simple and accessible interface for performing encryption, decryption, digital signatures, and verification, suitable for exploring post-quantum cryptographic methods.

## Features

- **Public-key Encryption**: Lattice-based encryption scheme inspired by Kyber.
- **Digital Signatures**: Lattice-based signature scheme inspired by Dilithium.
- **Benchmarking**: Measure the performance of encryption, decryption, signing, and verification operations.
- **Unit Testing**: Ensure the correctness of cryptographic operations with built-in tests.

## Installation

You can install `pqct` using pip. To install from the Python Package Index (PyPI):

```bash
pip install pqct
```

To install directly from the GitHub repository:

```bash
pip install git+https://github.com/G4G4N/pqct.git
```

## Usage

### Importing the Toolkit

First, import the `PostQuantumCryptoToolkit` from the `pqct` package.

```python
from pqct import PostQuantumCryptoToolkit
```

### Encryption and Decryption

To use the Kyber-inspired encryption scheme:

```python
import numpy as np
from pqct import PostQuantumCryptoToolkit

# Initialize the toolkit
toolkit = PostQuantumCryptoToolkit()

# Define plaintext (e.g., a list of integers)
plaintext = np.random.randint(0, 3329, 256)

# Generate keypair
public_key, private_key = toolkit.supported_algorithms['kyber'].generate_keypair()

# Encrypt the plaintext
ciphertext = toolkit.encrypt('kyber', plaintext)

# Decrypt the ciphertext
decrypted_plaintext = toolkit.decrypt('kyber', ciphertext, private_key)

# Verify decryption correctness
assert np.array_equal(decrypted_plaintext, plaintext), "Decryption failed"
```

### Digital Signatures

To use the Dilithium-inspired digital signature scheme:

```python
from pqct import PostQuantumCryptoToolkit

# Initialize the toolkit
toolkit = PostQuantumCryptoToolkit()

# Define message (e.g., a byte string)
message = b"Test message"

# Generate keypair
public_key, private_key = toolkit.supported_algorithms['dilithium'].generate_keypair()

# Sign the message
signature = toolkit.sign('dilithium', message)

# Verify the signature
is_valid = toolkit.verify('dilithium', message, signature, public_key)

# Verify signature correctness
assert is_valid, "Signature verification failed"
```

## Running Tests

The `pqct` package includes unit tests to verify the functionality of the cryptographic algorithms. You can run these tests using Python's built-in unittest framework.

```bash
python -m unittest discover pqct/tests
```

## Benchmarks

The package includes a benchmarking script to measure the performance of the cryptographic operations. Run the benchmarks with:

```bash
python benchmarks.py
```

## Project Structure

Here's a brief overview of the project structure:

- `pqct/` – Core directory containing the implementation files.
  - `__init__.py` – Initializes the `pqct` package.
  - `algorithms.py` – Contains the implementation of Kyber and Dilithium algorithms.
  - `toolkit.py` – Provides the interface to the cryptographic algorithms.
  - `tests.py` – Includes unit tests for verifying algorithm functionality.
- `benchmarks.py` – Script for benchmarking the cryptographic operations.
- `requirements.txt` – Lists the dependencies required by the project.
- `setup.py` – Setup configuration for packaging and distribution.
- `README.md` – Documentation for the project.

## Contributing

Contributions to `pqct` are welcome! If you have any suggestions, bug reports, or would like to contribute code, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Make your changes and commit them with descriptive messages.
4. Push your branch to your forked repository.
5. Open a pull request describing your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

For more information, please refer to the [documentation](https://github.com/yourusername/pqct) or contact the project maintainer.

```



