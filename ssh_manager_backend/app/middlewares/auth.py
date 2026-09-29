import base64
import io
import json
from typing import Dict

from werkzeug.wrappers import Request, Response

from ssh_manager_backend.app.controllers import api_controller
from ssh_manager_backend.app.models import Users
from ssh_manager_backend.app.services import utils
from ssh_manager_backend.db import User


class Auth:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)
        request_endpoint = request.split(-1)
        if request_endpoint in ["register", "login", "get_rsa_key"]:
            return self.app(environ, start_response)

        access_token: str = request.headers.get("access_token")
        content_length = int(environ.get("CONTENT_LENGTH"))
        request_body = environ["wsgi.input"].read(content_length).decode()
        request_body: Dict[str, any] = json.loads(json.loads(request_body))

        request_data, key, iv = api_controller.decrypt_request_data(body=request_body)

        if access_token is None:
            data = {"success": False}
            response = api_controller.response_data(
                data=data, message="Unauthorized", status_code=401, key=key, iv=iv
            )
            return response(environ, start_response)

        access_token: str = base64.decodebytes(
            bytes(access_token, encoding="utf-8")
        ).decode()
        username: str = access_token.split("+")[-1]
        user: User = Users().get_user(username=username)

        if user is None:
            data = {"success": False}
            response = api_controller.response_data(
                data=data, message="Unauthorized", status_code=401, key=key, iv=iv
            )
            return response(environ, start_response)

        if request_endpoint in ["grant_access", "revoke_access"]:
            if not user.admin:
                data = {"success": False}
                response = api_controller.response_data(
                    data=data, message="Unauthorized", status_code=401, key=key, iv=iv
                )
                return response(environ, start_response)

            user_password: str = request_data["password"]
            password_hash: bytes = utils.hash_data(
                data=user_password, salt=user.salt_for_password
            )

            if password_hash != user.password:
                data = {"success": False}
                response = api_controller.response_data(
                    data=data,
                    message="Authorization Failed",
                    status_code=401,
                    key=key,
                    iv=iv,
                )
                return response(environ, start_response)

        return self.app(environ, start_response)
