import base64
import uuid
from typing import Dict, Union

from flask import Response

from ssh_manager_backend.app.controllers import api_controller as api
from ssh_manager_backend.app.controllers.secrets import Secrets
from ssh_manager_backend.app.models import Sessions, Users
from ssh_manager_backend.app.services import utils
from ssh_manager_backend.db import User


class UserController:
    def __init__(self, access_token: Union[str, None] = None):
        self.username: str = ""
        if access_token is not None:
            access_token = base64.decodebytes(
                bytes(access_token, encoding="utf-8")
            ).decode()
            self.username = access_token.split("+")[-1]
        self.secrets = Secrets()
        self.__password: str = ""
        self.name: str = ""
        self.admin: str = ""
        self.user = Users()

    def set_attributes(self, username: str, password: str, name: str):
        """
        Sets the class attribute based on the function arguments.

        :param username: The username of the user
        :param password: The password of the user
        :param name: The name of the user
        :return:
        """

        self.username = username
        self.__password = password
        self.name = name

    def register(self, body: Dict[str, any]) -> Response:
        """
        Generates the secrets of the user based on the password. Hashes the password using SAH256 and stores the
        generated information in DynamoDB.

        :param body:
        :return: True/False for success/failure
        """

        data, key, iv = api.decrypt_request_data(body=body)
        self.set_attributes(
            username=data["username"], password=data["password"], name=data["name"]
        )

        if self.user.exists(username=self.username):
            data = {"success": False}
            return api.response_data(
                data=data, message="Username is taken", status_code=409, key=key, iv=iv
            )

        self.secrets.generate_secrets(password=str(self.__password))
        self.__password = utils.hash_data(
            self.__password, self.secrets.salt_for_password
        )
        user_is_admin = True

        if self.user.admin_exists():
            user_is_admin = False

        user_created = self.user.create(
            name=self.name,
            username=self.username,
            password=self.__password,
            admin=user_is_admin,
            encrypted_dek=self.secrets.dek,
            iv_for_dek=self.secrets.iv_for_dek,
            salt_for_dek=self.secrets.salt_for_dek,
            iv_for_kek=self.secrets.iv_for_kek,
            salt_for_kek=self.secrets.salt_for_kek,
            salt_for_password=self.secrets.salt_for_password,
        )

        data = {"success": user_created}
        return api.response_data(
            data=data, message="User created", status_code=200, key=key, iv=iv
        )

    def login(self, body: Dict[str, any]) -> Response:
        """
        Handles user login.

        :param body:
        :return: access token upon successful login
        """

        data, key, iv = api.decrypt_request_data(body=body)
        self.set_attributes(
            username=data["username"], password=data["password"], name=""
        )

        user: User = self.user.get_user(self.username)

        if user is None:
            data = {"success": False}
            return api.response_data(
                data=data,
                message="User does not exists",
                status_code=401,
                key=key,
                iv=iv,
            )

        user_data = user
        self.set_attributes(
            username=self.username, password=self.__password, name=user_data.name
        )
        secrets = {
            "encryptedDek": user_data.encrypted_dek,
            "ivForDek": user_data.iv_for_dek,
            "saltForDek": user_data.salt_for_dek,
            "ivForKek": user_data.iv_for_kek,
            "saltForKek": user_data.salt_for_kek,
            "saltForPassword": user_data.salt_for_password,
        }
        self.secrets.set_secrets(secrets=secrets)

        if user_data.password == utils.hash_data(
            data=self.__password, salt=self.secrets.salt_for_password
        ):
            access_token: str = uuid.uuid4().hex + "+" + self.username
            access_token = (
                base64.encodebytes(bytes(access_token, encoding="utf-8"))
                .decode()
                .strip()
            )
            session = Sessions()

            res = True
            if not session.exists(username=self.username):
                res = session.create(username=self.username, access_token=access_token)
            else:
                res = session.activate_session(username=self.username)

            if res:
                data = {"success": True, "access_token": access_token}
                return api.response_data(
                    data=data,
                    message="Login successful",
                    status_code=200,
                    key=key,
                    iv=iv,
                )
        else:
            data = {
                "success": False,
            }
            return api.response_data(
                data=data,
                message="Password does not match",
                status_code=401,
                key=key,
                iv=iv,
            )

    def logout(self, body: Dict[str, any]):
        """
        Handles user logout.

        Args:
            body:
            access_token:

        Returns:

        """

        _, key, iv = api.decrypt_request_data(body=body)

        if self.user.exists(username=self.username):
            session = Sessions()

            if not session.exists(username=self.username):
                data = {"success": False}
                return api.response_data(
                    data=data,
                    message="User not logged in",
                    status_code=400,
                    key=key,
                    iv=iv,
                )
            else:
                if session.deactivate_session(username=self.username):
                    data = {"success": True}
                    return api.response_data(
                        data=data,
                        message="Log out successful",
                        status_code=200,
                        key=key,
                        iv=iv,
                    )

        data = {"success": False}
        return api.response_data(
            data=data,
            message="User not found",
            status_code=404,
            key=key,
            iv=iv,
        )

    def is_admin(self, body: Dict[str, any]) -> Response:
        """
        Checks whether user is admin or not.

        Args:
            body:
            access_token:

        Returns:

        """

        data, key, iv = api.decrypt_request_data(body=body)

        user = self.user.get_user(username=self.username)

        data = {"success": True, "is_admin": user is not None and user.admin}
        return api.response_data(data=data, message="", status_code=200, key=key, iv=iv)

    def is_logged_in(self, body: Dict[str, any], access_token: Union[str]) -> Response:
        """
        Checks whether user is logged in or not.

        Args:
            body:
            access_token:

        Returns:

        """

        _, key, iv = api.decrypt_request_data(body=body)

        session = Sessions()

        data = {"Success": True, "is_logged_in": session.is_active(self.username)}
        return api.response_data(data=data, message="", status_code=200, key=key, iv=iv)
