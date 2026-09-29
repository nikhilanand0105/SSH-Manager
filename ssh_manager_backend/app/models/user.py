from typing import Union

from sqlalchemy.exc import SQLAlchemyError

from ssh_manager_backend.db import User
from ssh_manager_backend.db.database import db_session


class Users:
    def __init__(self):
        self.session = db_session()

    def exists(self, username: str) -> bool:
        """
        Checks whether a username exists in db.

        :param username:
        :return: boolean value indicating presence of username.
        """

        return (
            self.session.query(User).filter(User.username == username).first()
            is not None
        )

    def password_hash(self, username: str) -> Union[str, None]:
        """
        Gets the password hash corresponding to the given username.

        :param username:
        :return: stored password hash.
        """

        try:
            password_hash: str = (
                self.session.query(User)
                .filter(User.username == username)
                .first()
                .password
            )
            return password_hash
        except AttributeError:
            return None

    def admin_exists(self) -> bool:
        """
        Checks whether an admin exists.

        :return: boolean value indicating the presence of an admin.
        """

        return self.session.query(User).filter(User.admin is True).first() is not None

    def create(
        self,
        name: str,
        username: str,
        password: bytes,
        admin: bool,
        encrypted_dek: bytes,
        iv_for_dek: bytes,
        salt_for_dek: bytes,
        iv_for_kek: bytes,
        salt_for_kek: bytes,
        salt_for_password: bytes,
    ) -> bool:
        """
        Creates a user in database.

        :param name:
        :param username:
        :param password:
        :param admin:
        :param encrypted_dek:
        :param iv_for_dek:
        :param salt_for_dek:
        :param iv_for_kek:
        :param salt_for_kek:
        :param salt_for_password:
        :return: Boolean value indicating success/failure.
        """

        try:
            user = User()
            user.name = name
            user.username = username
            user.password = password
            user.admin = admin
            user.encrypted_dek = encrypted_dek
            user.iv_for_dek = iv_for_dek
            user.salt_for_dek = salt_for_dek
            user.iv_for_kek = iv_for_kek
            user.salt_for_kek = salt_for_kek
            user.salt_for_password = salt_for_password

            self.session.add(user)
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            return False

        return True

    def password_match(self, username: str, password: bytes) -> bool:
        """
        Checks whether the given password matches the password corresponding to the username.

        :param username:
        :param password:
        :return: boolean value indicating whether password matches or not.
        """

        try:
            user_password: str = (
                self.session.query(User)
                .filter(User.username == username)
                .first()
                .password
            )
            return user_password == password
        except AttributeError:
            return False

    def get_user(self, username: str) -> Union[None, User]:
        """
        Gets the key object from teh database.

        :param username:
        :return: User object
        """

        return self.session.query(User).filter(User.username == username).first()

    def destroy_user(self, username: str) -> bool:
        """
        Deletes a user.

        :param username:
        :return: Boolean value indicating success/failure.
        """

        try:
            user: User = (
                self.session.query(User).filter(User.username == username).first()
            )
            self.session.delete(user)
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            return False

        return True
