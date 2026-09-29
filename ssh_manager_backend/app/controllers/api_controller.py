import base64
import json
from typing import Dict, Tuple

from flask import Response

from ssh_manager_backend.app.services import AES, rsa


def response_data(
    data: Dict[str, any], message: str, status_code: int, key: bytes, iv: bytes
) -> Response:
    """

    Args:
        data: Response data.
        message: Response message.
        status_code:
        key: Key to be used for encrypting the response.
        iv: Initialization vector.

    Returns: Response

    """

    body: Dict[str, any] = {
        "data": base64.encodebytes(
            encrypt_response_data(data=data, key=key, iv=iv)
        ).decode(),
        "message": message,
    }

    return Response(
        response=json.dumps(body), status=status_code, mimetype="application/json"
    )


def encrypt_response_data(data: Dict[str, any], key: bytes, iv: bytes) -> bytes:
    """
    Encrypts the response data using the given key and iv.

    Args:
        data: Data to be encrypted.
        key: Key used for encryption
        iv: Initialization vector

    Returns: Encrypted data

    """

    aes = AES(key=key, iv=iv)
    return aes.encrypt(json.dumps(data))


def decrypt_request_data(body: Dict[str, any]) -> Tuple[Dict[str, any], bytes, bytes]:
    """
    Decrypts the request data using the RSA private key.

    Args:
        body: request body.

    Returns: decrypted request data

    """

    encrypted_key: bytes = base64.decodebytes(bytes(body["key"], encoding="utf-8"))
    encrypted_iv: bytes = base64.decodebytes(bytes(body["iv"], encoding="utf-8"))
    encrypted_data: bytes = base64.decodebytes(bytes(body["data"], encoding="utf-8"))

    key: bytes = rsa.decrypt_cipher(encrypted_key)
    iv: bytes = rsa.decrypt_cipher(encrypted_iv)

    aes = AES(key=key, iv=iv)
    data: str = aes.decrypt(encrypted_data).decode("utf-8")
    return json.loads(data), key, iv
