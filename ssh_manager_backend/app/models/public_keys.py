from typing import Union

from sqlalchemy.exc import SQLAlchemyError

from ssh_manager_backend.db import PublicKey
from ssh_manager_backend.db.database import db_session


class PublicKeys:
    def __init__(self):
        self.session = db_session()

    def exists(self, key_hash: bytes) -> bool:
        """
        Checks whether key with the given name exists.

        :param key_hash:
        :return: boolean value indicating the presence of key.
        """

        return (
            self.session.query(PublicKey).filter(PublicKey.key_hash == key_hash).first()
            is not None
        )

    def create(self, public_key: bytes, key_hash: str, user_id: int) -> bool:
        """
        Creates a key in database.

        :param public_key:
        :param key_hash:
        :param user_id:
        :return: Boolean value indicating success/failure.
        """

        try:
            key: PublicKey = PublicKey(
                public_key=public_key,
                key_hash=key_hash,
                user_id=user_id,
            )

            self.session.add(key)
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            return False

        return True

    def get_key(self, key_hash: bytes) -> Union[None, PublicKey]:
        """
        Gets the key object from teh database.

        :param key_hash:
        :return: PublicKey object
        """

        return (
            self.session.query(PublicKey).filter(PublicKey.key_hash == key_hash).first()
        )

    def delete_key(self, key_hash: bytes) -> bool:
        """
        Deletes a private key.

        Args:
            key_hash:

        Returns:

        """

        try:
            self.session.query(PublicKey).filter(
                PublicKey.key_hash == key_hash
            ).delete()
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            return False

        return True
