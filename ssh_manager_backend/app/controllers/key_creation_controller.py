import base64
from typing import Dict, Union

from flask import Response

from ssh_manager_backend.app.controllers import api_controller as api
from ssh_manager_backend.app.models import PrivateKeys, PublicKeys, Users
from ssh_manager_backend.app.services import AES, utils
from ssh_manager_backend.db import User


class KeyCreationController:
    def __init__(self, access_token: str):
        access_token: str = base64.decodebytes(
            bytes(access_token, encoding="utf-8")
        ).decode()
        self.username: str = access_token.split("+")[-1]
        self.password: Union[str, bytes, None] = None

        self.iv_for_kek: Union[bytes, None] = None
        self.salt_for_kek: Union[bytes, None] = None
        self.encrypted_dek: Union[bytes, None] = None
        self.iv_for_dek: Union[bytes, None] = None
        self.salt_for_dek: Union[bytes, None] = None
        self.dek: Union[bytes, None] = None

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

    def encrypt(self, plaintext: Union[str, bytes]) -> bytes:
        """
        Encrypts the SSH key with the "dek" and salt for "dek".

        :param plaintext: The text to be encrypted
        :return: ciphertext
        """

        dek_pbkdf = utils.pbkdf(data=self.dek, salt=self.salt_for_dek)
        aes = AES(key=dek_pbkdf, iv=self.iv_for_dek)
        ciphertext = aes.encrypt(plaintext=plaintext)

        return ciphertext

    def put_public_key(self, public_key: str, user_id: int):
        """
        Puts public key in the db.

        Args:
            public_key (str):
            user_id (int):
        """

        key_hash: bytes = utils.hash_data(data=public_key, salt=b"")
        PublicKeys().create(
            public_key=bytes(public_key, encoding="utf-8"),
            key_hash=key_hash,
            user_id=user_id,
        )

    def put_private_key(self, private_key: str, user_id):
        """
        Puts private key in the db.

        Args:
            private_key (str):
            user_id ([type]):
        """

        encrypted_private_key: bytes = self.encrypt(private_key)
        key_hash: bytes = utils.hash_data(data=private_key, salt=b"")

        PrivateKeys().create(
            encrypted_key=encrypted_private_key,
            key_hash=key_hash.decode(),
            user_id=user_id,
        )

    def put_keys(self, body: Dict[str, any]) -> Response:
        """
        Main function for storing keys in the db.

        Args:
            body (Dict[str, any]): Request body.

        Returns:
            Response:
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

        self.password = request_data["password"]
        public_key: str = request_data["public_key"]
        private_key: str = request_data["private_key"]

        if user.private_key is not None:
            data = {
                "success": False,
            }
            return api.response_data(
                data=data,
                message="User's key exists",
                status_code=409,
                key=key,
                iv=iv,
            )

        self.set_user_secrets(user=user)
        self.put_public_key(public_key=public_key)
        self.put_private_key(private_key=private_key)

        data = {"success": True}
        return api.response_data(
            data=data,
            message="Successfully stored the key",
            status_code=200,
            key=key,
            iv=iv,
        )
