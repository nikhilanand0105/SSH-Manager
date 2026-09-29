import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ssh_manager_backend.app.services.aes import AES


"""
ABBREVIATIONS:

kek = key encryption key
dek = decryption key
iv = initialization vector
"""


class Secrets:
    __csprnglength__ = 32
    __ivlength__ = 16

    def __init__(self):
        self.kek = None
        self.dek = None
        self.salt_for_dek = None
        self.iv_for_dek = None
        self.salt_for_kek = None
        self.iv_for_kek = None
        self.salt_for_password = None

    def set_secrets(self, secrets: dict):
        """
        Sets the value for class attributes based on the input

        Parameters
        ----------
        secrets: dict
            The secrets dictionary used for setting the class attributes
        ----------
        """

        self.dek = secrets["encryptedDek"]
        self.iv_for_dek = secrets["ivForDek"]
        self.salt_for_dek = secrets["saltForDek"]
        self.iv_for_kek = secrets["ivForKek"]
        self.salt_for_kek = secrets["saltForKek"]
        self.salt_for_password = secrets["saltForPassword"]

    @staticmethod
    def generate_secure_random(length: int) -> bytes:
        """
        Generated a cryptographically secure sequence of random bytes of the specified length

        :param length:
        """

        secure_random = os.urandom(length)
        return secure_random

    def generate_kek(self, password: str) -> bytes:
        """
        Generated key encryption key from the password using PBKDF2 (Password based key definition function)

        :param password:
        """

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt_for_kek,
            iterations=100000,
            backend=default_backend(),
        )

        return kdf.derive(bytes(password, encoding="utf-8"))

    def encrypt_dek(self) -> bytes:
        """
        Encrypts the decryption key from the user's password/kek
        """

        aes = AES(self.kek, self.iv_for_kek)
        return aes.encrypt(self.dek)

    def generate_secrets(self, password: str):
        """
        A utility function which calls the above functions for generating the value of secrets. This function is
        called during the registration phase.

        :param password:
        """

        self.salt_for_password = self.generate_secure_random(self.__csprnglength__)
        self.dek = self.generate_secure_random(self.__csprnglength__)
        self.salt_for_dek = self.generate_secure_random(self.__csprnglength__)
        self.iv_for_dek = self.generate_secure_random(self.__ivlength__)
        self.salt_for_kek = self.generate_secure_random(self.__csprnglength__)
        self.iv_for_kek = self.generate_secure_random(self.__ivlength__)
        self.kek = self.generate_kek(password)
        self.dek = self.encrypt_dek()
