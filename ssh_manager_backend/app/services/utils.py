from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


"""
This is sa utility file which contains functions which are called frequently in various files.
"""


def hash_data(data: str or bytes, salt: bytes) -> bytes:
    """
    Hashes the given data using the salt and returns the hashed bytes. If the provided data is not an instance of bytes, then an explicit conversion is done.

    Parameters
    ----------
    data: str, bytes
        The data to be hashed
    salt: bytes
        The salt used for hashing
    ----------
    """

    if not isinstance(data, bytes):
        data = bytes(data, encoding="utf-8") + salt

    digest = hashes.Hash(algorithm=hashes.SHA256(), backend=default_backend())

    digest.update(data)
    return digest.finalize()


def pbkdf(data: str or bytes, salt: bytes) -> bytes:
    """
    Generates a key from the data and salt using the PBKDF2(Password based key derivation function) algorithm and returns the generated key(in bytes)

    Parameters
    ----------
    data: str, bytes
        The password in the PBKDF
    salt: bytes
        The salt used for PBKDF
    ----------
    """

    if not isinstance(data, bytes):
        data = bytes(data, encoding="utf-8")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )

    return kdf.derive(data)
