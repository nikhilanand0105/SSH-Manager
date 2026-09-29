from typing import Union

from sqlalchemy.exc import SQLAlchemyError

from ssh_manager_backend.db import Session
from ssh_manager_backend.db.database import db_session


class Sessions:
    def __init__(self):
        self.session = db_session()

    def exists(self, username: str) -> bool:
        """
        Checks whether a session exists.

        :params username: The username of the user.
        :return:
        """

        return (
            self.session.query(Session).filter(Session.username == username).first()
            is not None
        )

    def create(self, username: str, access_token: str) -> bool:
        """
        Creates a user session and returns access token upon success.

        :param username: The username of the user,
        :param access_token:
        :return:
        """

        try:
            user_session = Session()
            user_session.username = username
            user_session.access_token = access_token
            user_session.active = True
            self.session.add(user_session)
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            return False
        except AttributeError:
            return False

        return True

    def activate_session(self, username: str) -> bool:
        """
        Activates a user session.
        :param username: The username of the user,
        :return:
        """

        try:
            self.session.query(Session).filter(Session.username == username).update(
                {"active": True}
            )
            self.session.commit()

            return True
        except AttributeError:
            return False

    def deactivate_session(self, username: str) -> bool:
        """
        Activates a user session.
        :param username: The username of the user,
        :return:
        """

        try:
            self.session.query(Session).filter(Session.username == username).update(
                {"active": False}
            )
            self.session.commit()
            return True
        except AttributeError:
            return False

    def user_access_token(self, username: str) -> Union[bool, str]:
        """
        Returns access token of user.

        :param username: The username of the user,
        :return: access token
        """

        try:
            access_token = (
                self.session.query(Session)
                .filter(Session.username == username)
                .first()
                .access_token
            )
            return access_token
        except AttributeError:
            return False

    def is_active(self, username: str) -> bool:
        """
        Checks whether a session is active or not.

        Args:
            username:

        Returns:

        """

        try:
            is_active: bool = (
                self.session.query(Session)
                .filter(Session.username == username)
                .first()
                .active
            )
            return is_active
        except AttributeError:
            return False
