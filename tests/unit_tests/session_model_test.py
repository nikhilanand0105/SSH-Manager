import pytest

from ssh_manager_backend.app.models import SessionModel, UserModel
from tests.test_ssh_manager_backend import db_cleanup


class TestSessionModel:
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

        session = SessionModel()
        access_token: str = "test_access_token"

        assert session.create(username=username, access_token=access_token) is False

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

        assert session.create(username=username, access_token=access_token) is True

    def test_exists(self):
        username: str = "test_username"
        session = SessionModel()

        assert session.exists(username=username) is True
        assert session.exists(username="non_existent_usernmae") is False

    def test_activate(self):
        username: str = "test_username"
        session = SessionModel()

        assert session.activate_session(username=username) is True

    def test_deactivate(self):
        username: str = "test_username"
        session = SessionModel()

        assert session.deactivate_session(username=username) is True

    def test_access_token(self, cleanup):
        username: str = "test_username"
        session = SessionModel()

        assert isinstance(session.access_token(username=username), str)
        assert session.access_token(username="non_existent_usernmae") is False
