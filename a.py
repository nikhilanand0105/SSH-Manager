# from ssh_manager_backend.app.models import SessionModel, UserModel

# user = UserModel()
# name: str = "test_user"
# username: str = "test_username"
# password: str = b"test_password"
# admin: bool = False
# encrypted_dek: bytes = b"test_encrypted_dek"
# iv_for_dek: bytes = b"test_iv_for_dek"
# salt_for_dek: bytes = b"test_salt_for_dek"
# iv_for_kek: bytes = b"test_iv_for_kek"
# salt_for_kek: bytes = b"test_salt_for_kek"
# salt_for_password: bytes = b"test_salt_for_password"

# session = SessionModel()
# access_token: str = "test_access_token"

# session = SessionModel()
# user = UserModel()
# user.create(
#     name=name,
#     username=username,
#     password=password,
#     admin=admin,
#     encrypted_dek=encrypted_dek,
#     iv_for_dek=iv_for_dek,
#     salt_for_dek=salt_for_dek,
#     iv_for_kek=iv_for_kek,
#     salt_for_kek=salt_for_kek,
#     salt_for_password=salt_for_password,
# )
# session.create(username=username, access_token=access_token)

from ssh_manager_backend.app.controllers import key_mapping
from tests.test_ssh_manager_backend import db_cleanup

key_mapping.store_mapping()
