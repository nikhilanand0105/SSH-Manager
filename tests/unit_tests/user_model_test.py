import pytest

from ssh_manager_backend.app.models.user import User
from ssh_manager_backend.db import User
from tests.test_ssh_manager_backend import db_cleanup


class TestUser:
    @pytest.fixture
    def cleanup(self):
        yield
        db_cleanup()

    def test_create(self):
        user = User()
        name: str = "test_user"
        username: str = "test_username"
        password: bytes = b"test_password"
        admin: bool = False
        encrypted_dek: bytes = b"test_encrypted_dek"
        iv_for_dek: bytes = b"test_iv_for_dek"
        salt_for_dek: bytes = b"test_salt_for_dek"
        iv_for_kek: bytes = b"test_iv_for_kek"
        salt_for_kek: bytes = b"test_salt_for_kek"
        salt_for_password: bytes = b"test_salt_for_password"

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
            is False
        )

    def test_admin_exist(self):
        user = User()
        assert user.admin_exists() is False

    def test_password_hash(self):
        user = User()
        username: str = "test_username"
        password: str = b"test_password"
        assert user.password_hash("non_existent_username") is None
        assert user.password_hash(username) == password

    def test_exists(self):
        user = User()
        username: str = "test_username"
        assert user.exists("non_existent_username") is False
        assert user.exists(username) is True

    def test_get_user(self):
        user = User()
        username: str = "test_username"
        assert user.get_user("non_existent_username") is None
        assert isinstance(user.get_user(username), User) is True
        print(User)

    def test_destroy_user(self, cleanup):
        user = User()
        username: str = "test_username"
        assert user.destroy_user("non_existent_username") is False
        assert user.destroy_user(username) is True
