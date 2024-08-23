# setup.py

from setuptools import setup, find_packages

setup(
    name="post-quantum-crypto-toolkit",
    version="0.1.0",
    author="Gagan Yalamuri",
    author_email="gagan.y@nyu.com",
    description="A Python toolkit for post-quantum cryptographic algorithms",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/G4G4N/post-quantum-crypto-toolkit",
    packages=find_packages(),
    install_requires=[
        "pqcrypto",
        "numpy"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
