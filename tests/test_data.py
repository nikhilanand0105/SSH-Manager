import base64
import json
import os
from typing import Dict

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from ssh_manager_backend.app.services import AES, RSA

base_url = "http://localhost:5000/"

request_encryption_key: bytes = os.urandom(32)
request_encryption_iv: bytes = os.urandom(16)
aes = AES(key=request_encryption_key, iv=request_encryption_iv)
rsa = RSA()

name: str = "test_user"
username: str = "test_username"
password: str = "test_password"
admin: bool = False
encrypted_dek: bytes = b"test_encrypted_dek"
iv_for_dek: bytes = b"test_iv_for_dek"
salt_for_dek: bytes = b"test_salt_for_dek"
iv_for_kek: bytes = b"test_iv_for_kek"
salt_for_kek: bytes = b"test_salt_for_kek"
salt_for_password: bytes = b"test_salt_for_password"


def get_rsa_key():
    res = requests.get(base_url + "get_rsa_key").json()
    return res["data"]["public_key"]


def encrypt_data(rsa_key: str, plaintext: bytes):
    public_key = serialization.load_pem_public_key(
        data=bytes(rsa_key, encoding="utf-8"), backend=default_backend()
    )
    print(public_key)
    return public_key.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None
        ),
    )


def get_request_data(data: bytes, key: bytes, iv: bytes):
    request_data = {
        "data": base64.encodebytes(data).decode(),
        "key": base64.encodebytes(key).decode(),
        "iv": base64.encodebytes(iv).decode(),
    }

    return request_data
