from typing import List, Union

from sqlalchemy.exc import SQLAlchemyError

from ssh_manager_backend.db import AccessControl, User
from ssh_manager_backend.db.database import db_session


class AccessControlModel:
    def __init__(self):
        self.session = db_session()

    def create(self, username: str):
        """
        Creates an entry in the access_control table for the given user.

        :param username
        :return: boolean value whether the entry is created or not.
        """

        try:
            acl_details: AccessControl = AccessControl(
                username=username, ip_addresses=[]
            )
            self.session.add(acl_details)
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            return False

        return True

    def has_access(self, username: str, ip_address: str) -> Union[bool, None]:
        """
        Checks whether a user has access to the provided the list of ip addresses.

        :param username:
        :param ip_address:
        :return: boolean value stating whether user has access or not.
        """

        try:
            acl_details: AccessControl = (
                self.session.query(AccessControl)
                .filter(AccessControl.username == username)
                .first()
            )
            return ip_address in acl_details.ip_addresses
        except [AttributeError, SQLAlchemyError]:
            return None

    def grant_access(self, username: str, ip_addresses: List[str]) -> bool:
        """
        Updates user access.

        :param username:
        :param ip_addresses:
        :return: booleans value for success/failure.
        """

        try:
            acl_details: AccessControl = (
                self.session.query(AccessControl, User)
                .join(User)
                .filter(AccessControl.username == username)
                .first()
            )

            acl_details.ip_addresses += ip_addresses
            acl_details.ip_addresses = list(set(acl_details.ip_addresses))

            self.session.query(AccessControl).filter(
                AccessControl.username == username
            ).update({"ip_addresses": acl_details.ip_addresses})

            self.session.commit()
        except AttributeError:
            return False
        except SQLAlchemyError:
            self.session.rollback()
            return False

        return True

    def revoke_access(
        self, username: str, ip_addresses: List[str], revoke_all: bool = False
    ) -> bool:
        """
        Updates user access.

        :param username:
        :param ip_addresses:
        :param revoke_all:.
        :return: booleans value for success/failure.
        """

        try:
            acl_details: AccessControl = (
                self.session.query(AccessControl)
                .join(User)
                .filter(AccessControl.username == username)
                .first()
            )

            if not revoke_all:
                for ip in ip_addresses:
                    try:
                        acl_details.ip_addresses.remove(ip)
                    except ValueError:
                        continue

                self.session.query(AccessControl).filter(
                    AccessControl.username == username
                ).update({"ip_addresses": acl_details.ip_addresses})
            else:
                self.session.query(AccessControl).filter(
                    AccessControl.username == username
                ).update({"ip_addresses": []})

            self.session.commit()
        except AttributeError:
            return False
        except SQLAlchemyError:
            self.session.rollback()
            return False

        return True

    def get_all_ips(self, username: str) -> List[str]:
        """
        Gets list of all Ip addresses for the given user.

        :param username:
        :return: list of ip addresses.
        """

        try:
            acl_details: AccessControl = (
                self.session.query(AccessControl)
                .join(User)
                .filter(AccessControl.username == username)
                .first()
            )
            return acl_details.ip_addresses
        except (AttributeError, SQLAlchemyError):
            return []
