from typing import Union

from cryptography.exceptions import InvalidKey, InvalidSignature, UnsupportedAlgorithm
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


"""This module is a wrapper around the Cipher class of cryptography.hazmat.primitives.ciphers. It make the process of
encryption and decryption of data using AES easier and can be achieved by just making an object of the class and just
calling the respective function. """


class AES:
    def __init__(self, key: bytes, iv: bytes):

        self.cipher = Cipher(
            algorithm=algorithms.AES(key), mode=modes.CBC(iv), backend=default_backend()
        )

    def encrypt(self, plaintext: Union[str, bytes]) -> bytes:
        """
        This function encrypts the data and return the ciphertext(in bytes)

        In case the input is a string, it is converted to bytes. After that the input is padded in order to make its
        length a multiple of 16 which is necessary for AES

        :param plaintext: The data to be encrypted
        :return: ciphertext
        """

        if not isinstance(plaintext, bytes):
            plaintext = bytes(str(plaintext), encoding="utf-8")

        padder = padding.PKCS7(128).padder()
        padded_plaintext = padder.update(plaintext) + padder.finalize()

        encryptor = self.cipher.encryptor()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        return ciphertext

    def decrypt(self, ciphertext: bytes) -> Union[bool, bytes]:
        """
        This function decrypts the data and returns plaintext(in bytes) in case of successful decryption else it
        returns false.

        First the ciphertext is decrypted to retrieve the padded plaintext. Then we un-pad the decrypted ciphertext to
        get the original plaintext. In case the key/padding is incorrect an exception is raised and False is returned.

        :param ciphertext: The encrypted data that needs to be decrypted
        :return: plaintext
        """

        try:
            unpadder = padding.PKCS7(128).unpadder()

            decrypter = self.cipher.decryptor()
            plaintext = decrypter.update(ciphertext) + decrypter.finalize()

            unpadded_plaintext = unpadder.update(plaintext) + unpadder.finalize()

            return unpadded_plaintext
        except UnsupportedAlgorithm or InvalidKey or InvalidSignature:
            return False
