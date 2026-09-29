import base64
from typing import Dict, Union

from flask import Response

from ssh_manager_backend.app.controllers import api_controller as api
from ssh_manager_backend.app.models import PrivateKeys, Users
from ssh_manager_backend.app.services import AES, utils
from ssh_manager_backend.db import PrivateKey, User


"""
This module manages the SSH key of the user.
"""


class PrivateKeyController:
    def __init__(self, access_token: str):
        access_token: str = base64.decodebytes(
            bytes(access_token, encoding="utf-8")
        ).decode()
        self.username: str = access_token.split("+")[-1]
        self.password: Union[str, bytes, None] = None
        self.key = PrivateKeys()

        self.iv_for_kek: Union[bytes, None] = None
        self.salt_for_kek: Union[bytes, None] = None
        self.encrypted_dek: Union[bytes, None] = None
        self.iv_for_dek: Union[bytes, None] = None
        self.salt_for_dek: Union[bytes, None] = None
        self.dek: Union[bytes, None] = None

        self.ssh_encrypted_key: Union[bytes, None] = None
        self.ssh_key: Union[bytes, None] = None

    def set_user_secrets(self, user: User):
        """
        Sets user secrets.

        Args:
            user:

        Returns:

        """

        self.iv_for_kek = user.iv_for_kek
        self.salt_for_kek = user.salt_for_kek
        self.encrypted_dek = user.encrypted_dek
        self.iv_for_dek = user.iv_for_dek
        self.salt_for_dek = user.salt_for_dek
        self.dek = self.decrypt_dek(password=self.password)

    def decrypt_dek(self, password: str) -> bytes:
        """
        Decrypts the dek(See secrets module) using AES and the password of the user.

        :param password: The password of the user
        :return: decrypted decryption key
        """

        kek = utils.pbkdf(data=password, salt=self.salt_for_kek)
        aes = AES(key=kek, iv=self.iv_for_kek)
        dek = aes.decrypt(self.encrypted_dek)
        return dek

    def decrypt(self, ciphertext):
        """
        Decrypts the SSH key using "dek" and salt for "dek" and AES algorithm.

        :param ciphertext: The text which is to be decrypted
        :return:
        """

        dek_pbkdf = utils.pbkdf(data=self.dek, salt=self.salt_for_dek)
        aes = AES(key=dek_pbkdf, iv=self.iv_for_dek)
        plaintext = aes.decrypt(ciphertext=ciphertext)

        return plaintext

    def get_private_key(self, body: Dict[str, any]) -> Response:
        """
        Gets the encrypted SSH key and decrypts it.

        :param body:
        :return:
        """

        request_data, key, iv = api.decrypt_request_data(body=body)

        user = Users().get_user(username=self.username)
        if user is None:
            data = {
                "success": False,
            }
            return api.response_data(
                data=data, message="Unauthorized", status_code=401, key=key, iv=iv
            )

        user_key: PrivateKey = user.private_key
        if user_key is None:
            data = {"success": False}

            return api.response_data(
                data=data,
                message="User's key does not exist",
                status_code=404,
                key=key,
                iv=iv,
            )

        self.password = request_data["password"]
        self.set_user_secrets()
        self.ssh_encrypted_key = user_key.encrypted_private_key
        self.ssh_key = self.decrypt(ciphertext=self.ssh_encrypted_key)

        data = {"success": False, "ssh_key": self.ssh_key}

        return api.response_data(data=data, message="", status_code=200, key=key, iv=iv)
