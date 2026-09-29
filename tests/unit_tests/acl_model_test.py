from typing import List

import pytest

from ssh_manager_backend.app.models.access_control import AccessControlModel
from ssh_manager_backend.app.models.user import UserModel
from tests.test_ssh_manager_backend import db_cleanup


class TestAccessControlModel:
    @pytest.fixture
    def cleanup(self):
        yield
        db_cleanup()

    def test_create(self):
        acl: AccessControlModel = AccessControlModel()
        user: UserModel = UserModel()

        name: str = "test_user"
        username = "test_username"
        password: str = b"test_password"
        admin: bool = False
        encrypted_dek: bytes = b"test_encrypted_dek"
        iv_for_dek: bytes = b"test_iv_for_dek"
        salt_for_dek: bytes = b"test_salt_for_dek"
        iv_for_kek: bytes = b"test_iv_for_kek"
        salt_for_kek: bytes = b"test_salt_for_kek"
        salt_for_password: bytes = b"test_salt_for_password"

        assert acl.create(username=username) is False

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

        assert acl.create(username=username) is True

    def test_grant_access(self):
        acl: AccessControlModel = AccessControlModel()
        username: str = "test_username"
        ip_addresses: List[str] = ["1.1.1.1", "1.0.0.1"]

        assert acl.grant_access(username=username, ip_addresses=ip_addresses) is True

        assert (
            acl.grant_access(
                username="non_existent_username", ip_addresses=ip_addresses
            )
            is False
        )

        assert sorted(acl.get_all_ips(username=username)) == sorted(ip_addresses)

    def test_revoke_access(self, cleanup):
        acl: AccessControlModel = AccessControlModel()
        username: str = "test_username"
        ip_addresses: List[str] = ["1.1.1.1", "1.0.0.1"]

        assert (
            acl.revoke_access(username=username, ip_addresses=[ip_addresses[0]]) is True
        )

        assert (
            acl.revoke_access(username=username, ip_addresses=["non_existent_ip"])
            is True
        )

        assert (
            acl.revoke_access(
                username="non_existent_username", ip_addresses=ip_addresses
            )
            is False
        )

        assert acl.get_all_ips(username=username) == [ip_addresses[1]]
