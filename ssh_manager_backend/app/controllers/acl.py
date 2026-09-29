import base64
from typing import Dict, List

from flask import Response

import tasks
from ssh_manager_backend.app.controllers import api_controller as api
from ssh_manager_backend.app.models import AccessControlModel, UserModel
from ssh_manager_backend.app.services import AES, utils
from ssh_manager_backend.db import Key, User


class AclController:
    def __init__(self, access_token: str):
        access_token = base64.decodebytes(
            bytes(access_token, encoding="utf-8")
        ).decode()
        self.admin_username = access_token.split("+")[-1]
        self.admin_user: User = UserModel().get_user(username=self.username)

    def grant_access(self, body: Dict[str, any]) -> Response:
        """
        Grants access to the given ip addresses.

        Args:
            body (Dict[str, any]):
        """

        data, key, iv = api.decrypt_request_data(body=body)
        grantee_username: str = data["username"]
        admin_password: str = data["password"]
        connection_strings: List[str] = data["connection_strings"]
        ip_addresses: List[str] = [
            connection_string.split("@")[1] for connection_string in connection_strings
        ]
        admin_ssh_key: bytes = self.get_ssh_key(password=admin_password)

        if admin_ssh_key == b"":
            data = {"success": False}
            return api.response_data(
                data=data,
                message="You haven't generated your key pair",
                status_code=409,
                key=key,
                iv=iv,
            )

        grantee_user: User = UserModel().get_user(username=grantee_username)

        if grantee_user is None:
            data = {"success": False}
            return api.response_data(
                data=data,
                message="The user you are trying to give access does not exist",
                status_code=404,
                key=key,
                iv=iv,
            )

        current_ips: List[str] = grantee_user.access_control.ip_addresses
        if ip_addresses in current_ips:
            data = {"success": False}
            return api.response_data(
                data=data,
                message="The user already has access.",
                status_code=409,
                key=key,
                iv=iv,
            )

        for connection_string in connection_strings:
            ip_address = connection_string.split("@")[1]
            remote_username = connection_string.split("@")[0]
            if ip_address not in current_ips:
                tasks.grant_access.delay(
                    grantee_username, admin_ssh_key, ip_address, remote_username
                )

        return api.response_data(
            data=data, message="Access will be granted", status_code=200, key=key, iv=iv
        )

    def revoke_access(body: Dict[str, any]) -> Response:
        """
        Revokes access to the list of IP addresses to the specifies username,

        :param body:
        :param access_token:
        :return:
        """

        data, key, iv = api.decrypt_request_data(body=body)
        grantee_username: str = data["username"]
        admin_password: str = data["password"]
        connection_strings: List[str] = data["connection_strings"]
        ip_addresses: List[str] = [
            connection_string.split("@")[1] for connection_string in connection_strings
        ]
        admin_ssh_key: bytes = get_ssh_key(password=admin_password)

        if admin_ssh_key == b"":
            data = {"success": False}
            return api.response_data(
                data=data,
                message="You haven't generated your key pair",
                status_code=409,
                key=key,
                iv=iv,
            )

        grantee_user: User = UserModel().get_user(username=grantee_username)

        if grantee_user is None:
            data = {"success": False}
            return api.response_data(
                data=data,
                message="The user you are trying to revoke access from does not exist",
                status_code=404,
                key=key,
                iv=iv,
            )

        current_ips: List[str] = grantee_user.access_control.ip_addresses
        if ip_addresses not in current_ips:
            data = {"success": False}
            return api.response_data(
                data=data,
                message="The user already does not has access.",
                status_code=409,
                key=key,
                iv=iv,
            )

        if current_ips is None:
            data = {"success": False}
            return api.response_data(
                data=data,
                message="Username does not exist",
                status_code=404,
                key=key,
                iv=iv,
            )

        for connection_string in connection_strings:
            ip_address = connection_string.split("@")[1]
            remote_username = connection_string.split("@")[0]
            if ip_address in current_ips:
                tasks.revoke_access.delay(
                    grantee_username, admin_ssh_key, ip_address, remote_username
                )

        data = {"success": True}
        return api.response_data(
            data=data, message="Access will be revoked", status_code=200, key=key, iv=iv
        )

    def revoke_all(body: Dict[str, any], access_token: str) -> Response:
        """
        Revokes all access of the specified user.

        :param body:
        :param access_token:
        :return:
        """

        data, key, iv = api.decrypt_request_data(body=body)
        grantee_username: str = data["username"]
        admin_password: str = data["password"]
        ssh_key: bytes = get_ssh_key(password=admin_password)

        if admin_ssh_key == b"":
            data = {"success": False}
            return api.response_data(
                data=data,
                message="You haven't generated your key pair",
                status_code=409,
                key=key,
                iv=iv,
            )

        grantee_user: User = UserModel().get_user(username=grantee_username)

        if grantee_user is None:
            data = {"success": False}
            return api.response_data(
                data=data,
                message="The user you are trying to revoke access from does not exist",
                status_code=404,
                key=key,
                iv=iv,
            )

        current_ips = AccessControlModel().get_all_ips(username=username)
        if current_ips is None:
            data = {"success": False}
            return api.response_data(
                data=data,
                message="Username does not exist",
                status_code=404,
                key=key,
                iv=iv,
            )

        for ip_address in current_ips:
            tasks.revoke_access.delay(username, ssh_key, ip_address)

        data = {"success": True}
        return api.response_data(
            data=data, message="Access will be revoked", status_code=200, key=key, iv=iv
        )

    def get_ssh_key(self, password: str) -> bytes:
        """
        Gets the ssh key from the access token of the user.

        Args:
            password (str):
        """

        kek: bytes = utils.pbkdf(data=password, salt=self.admin_user.salt_for_password)
        dek: bytes = AES(key=kek, iv=self.admin_user.iv_for_kek).decrypt(
            self.admin_user.encrypted_dek
        )

        user_key: Key = self.admin_user.private_key
        if not user_key:
            return b""

        encrypted_ssh_key: bytes = user_key.encrypted_private_key
        dek_pbkdf: bytes = utils.pbkdf(data=dek, salt=self.admin_user.salt_for_dek)
        aes = AES(key=dek_pbkdf, iv=self.admin_user.iv_for_dek)
        ssh_key: bytes = aes.decrypt(ciphertext=encrypted_ssh_key)

        return ssh_key
