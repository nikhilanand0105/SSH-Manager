import base64
import json
import sys

import pytest
import requests

from tests import test_data
from tests.test_ssh_manager_backend import db_cleanup

sys.path.append("../../")


class TestUserController:
    @pytest.fixture
    def cleanup(self):
        yield
        db_cleanup()

    def test_user_controller(self, cleanup):
        rsa_key = test_data.get_rsa_key()
        name = test_data.name
        username = test_data.username
        password = test_data.password

        data = json.dumps({"username": username, "password": password, "name": name})

        data = test_data.aes.encrypt(data)
        key = test_data.encrypt_data(
            rsa_key=rsa_key, plaintext=test_data.request_encryption_key
        )
        iv = test_data.encrypt_data(
            rsa_key=rsa_key, plaintext=test_data.request_encryption_iv
        )
        request_data = test_data.get_request_data(data=data, key=key, iv=iv)
        requests.post(test_data.base_url + "/register", json=json.dumps(request_data))

        data = json.dumps({"username": username, "password": password})

        data = test_data.aes.encrypt(data)
        request_data = test_data.get_request_data(data=data, key=key, iv=iv)
        res = requests.post(
            test_data.base_url + "/login", json=json.dumps(request_data)
        )

        data = json.loads(
            test_data.aes.decrypt(
                ciphertext=base64.decodebytes(
                    bytes(res.json()["data"], encoding="utf-8")
                )
            )
        )

        access_token = data["access_token"]

        data = json.dumps({})
        data = test_data.aes.encrypt(data)
        request_data = test_data.get_request_data(data=data, key=key, iv=iv)
        requests.post(
            test_data.base_url + "/logout",
            json=json.dumps(request_data),
            headers={"access_token": access_token},
        )
