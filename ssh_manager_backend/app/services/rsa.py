import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


"""
This is wrapper around rsa class of cryptography.hazmat.primitives.asymmetric and provides the functionality of
generating RSA key-pair, serializing the public key, decrypting a cipher using the private key and refreshing
the kye-pair.
"""


class RSA:
    def __init__(self):
        self._private_key = None
        self._public_key = None
        self.generation_time = 0
        self.expire_time = 3600  # (in seconds)

    def generate_key_pair(self) -> None:
        """
        Generates a 4096 bit RSA key-pair.

        :returns: None
        """

        self._private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=4096, backend=default_backend()
        )
        self.public_key = self._private_key.public_key()
        self.generation_time = time.time()

    def serialize_key(self) -> str:
        """
        Serializes the public key, encodes it to utf-8 format and returns it.

        :returns: serialized public key
        """

        public_key_serialized: bytes = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return public_key_serialized.decode("utf-8")

    def decrypt_cipher(self, ciphertext: bytes) -> bytes:
        """
        Decrypts the cipher encrypted from the generated RSA public key using the private key.

        :param ciphertext: The encrypted text to be decrypted
        :return: plaintext
        """

        plaintext: bytes = self._private_key.decrypt(
            ciphertext=ciphertext,
            padding=padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None
            ),
        )
        return plaintext

    @property
    def public_key(self) -> str:
        """
        Returns the serialized public key.
        """

        return self.serialize_key()

    def refresh_key_pair(self) -> None:
        """
        Refreshes the rsa key-pair.
        """

        self.generate_key_pair()

    def is_generated(self) -> bool:
        """
        Returns true is the key-pair is generated.
        """

        return self._private_key is not None

    @public_key.setter
    def public_key(self, value: bytes) -> None:
        """
        Sets the public key.

        :param value: The value of the public key.
        :return: None
        """

        self._public_key = value
