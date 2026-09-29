import pytest

from ssh_manager_backend.app.models.private_keys import KeyModel
from ssh_manager_backend.app.models.user import UserModel
from tests.test_ssh_manager_backend import db_cleanup


class TestKeyModel:
    @pytest.fixture
    def cleanup(self):
        yield
        db_cleanup()

    def test_create(self):
        user = UserModel()
        name: str = "test_user"
        username: str = "test_username"
        password: str = b"test_password"
        admin: bool = False
        encrypted_dek: bytes = b"test_encrypted_dek"
        iv_for_dek: bytes = b"test_iv_for_dek"
        salt_for_dek: bytes = b"test_salt_for_dek"
        iv_for_kek: bytes = b"test_iv_for_kek"
        salt_for_kek: bytes = b"test_salt_for_kek"
        salt_for_password: bytes = b"test_salt_for_password"

        key = KeyModel()
        key_name: str = "test_key"
        encrypted_key: bytes = b"encrypted_test_key"
        key_hash: str = "test_key_hash"

        assert (
            key.create(
                name=key_name,
                encrypted_key=encrypted_key,
                key_hash=key_hash,
                user_id=12345,
            )
            is False
        )

        assert (
            user.create(
                name=name,
                username=username,
                password=password,
                admin=admin,
                encrypted_dek=encrypted_dek,
                iv_for_dek=iv_for_dek,
                salt_for_dek=salt_for_dek,
                iv_for_kek=iv_for_kek,
                salt_for_kek=salt_for_kek,
                salt_for_password=salt_for_password,
            )
            is True
        )

        user_id = user.get_user(username=username).id

        assert (
            key.create(
                name=key_name,
                encrypted_key=encrypted_key,
                key_hash=key_hash,
                user_id=user_id,
            )
            is True
        )

    def test_exists(self):
        key = KeyModel()
        key_name: str = "test_key"

        assert key.exists(key_name=key_name) is True

        assert key.exists(key_name="non_existent_key") is False

    def test_get_key(self, cleanup):
        key = KeyModel()
        key_name: str = "test_key"

        assert key.get_key(key_name=key_name).name == key_name

        assert key.get_key(key_name="non_existent_keyname") is None
