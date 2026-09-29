import json
from typing import Dict

from flask import Blueprint, Response, request

from ssh_manager_backend.app.controllers import UserController
from ssh_manager_backend.app.services import rsa

rsa_ = Blueprint("rsa", __name__)
users_ = Blueprint("users", __name__)


@rsa_.route("/get_rsa_key", methods=["GET"])
def rsa_handler() -> Response:
    if not rsa.is_generated():
        rsa.generate_key_pair()

    return Response(response=json.dumps({"data": {"public_key": rsa.public_key}}))


@users_.route("/register", methods=["POST"])
def register_handler() -> Response:
    body: Dict[str, any] = json.loads(request.get_json())
    return UserController().register(body)


@users_.route("/login", methods=["POST"])
def login_handler() -> Response:
    body: Dict[str, any] = json.loads(request.get_json())
    return UserController().login(body)


@users_.route("/logout", methods=["POST"])
def logout_handler() -> Response:
    access_token: str = request.headers.get("access_token")
    body: Dict[str, any] = json.loads(request.get_json())
    return UserController(access_token=access_token).logout(body=body)


@users_.route("/is_admin", methods=["POST"])
def is_admin_handler() -> Response:
    body: Dict[str, any] = json.loads(request.get_json())
    access_token: str = request.headers.get("access_token")
    return UserController(access_token=access_token).is_admin(body=body)


@users_.route("/is_logged_in", methods=["POST"])
def is_logged_in():
    body: Dict[str, any] = json.loads(request.get_json())
    access_token: str = request.headers.get("access_token")
    return UserController(access_token=access_token).is_logged_in(body=body)
