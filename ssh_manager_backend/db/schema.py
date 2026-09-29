from sqlalchemy import ARRAY, Boolean, Column, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import relationship

from ssh_manager_backend.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    username = Column(String, unique=True)
    password = Column(LargeBinary)
    admin = Column(Boolean)
    encrypted_dek = Column(LargeBinary, unique=True)
    iv_for_dek = Column(LargeBinary, unique=True)
    salt_for_dek = Column(LargeBinary, unique=True)
    iv_for_kek = Column(LargeBinary, unique=True)
    salt_for_kek = Column(LargeBinary, unique=True)
    salt_for_password = Column(LargeBinary, unique=True)
    private_key = relationship("PrivateKey", cascade="all,delete", backref="users")
    public_key = relationship("PublicKey", cascade="all,delete", backref="users")
    access_control = relationship(
        "AccessControl", cascade="all,delete", backref="users"
    )
    session = relationship("Session", cascade="all,delete", backref="users")

    def __repr__(self) -> str:
        """
        :return: user id
        """

        return f"User {self.id}"


class PrivateKey(Base):
    __tablename__ = "private_keys"

    id = Column(Integer, primary_key=True)
    encrypted_private_key = Column(LargeBinary, unique=True)
    key_hash = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")

    def __repr__(self) -> str:
        """
        :return: key id
        """

        return f"Private Key {self.id}"


class PublicKey(Base):
    __tablename__ = "public_keys"

    id = Column(Integer, primary_key=True)
    public_key = Column(LargeBinary, unique=True)
    key_hash = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")

    def __repr__(self) -> str:
        """
        :return: key id
        """

        return f"Public Key {self.id}"


class PrivateKeyMapping(Base):
    __tablename__ = "private_key_mapping"

    id = Column(Integer, primary_key=True)
    private_key_id = Column(String, ForeignKey("private_keys.id"))
    ip_address = Column(String, unique=True)
    key = relationship("PrivateKey")

    def __repr__(self) -> str:
        """
        :return: key_mapping id
        """

        return f"Key Mapping {self.id}"


class AccessControl(Base):
    __tablename__ = "access_control"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    ip_addresses = Column(ARRAY(String))
    user = relationship("User")

    def __repr__(self) -> str:
        """
        :return: access_control id
        """

        return f"Access control {self.id}"


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey("users.username"))
    access_token = Column(String, unique=True)
    active = Column(Boolean)
    user = relationship("User")
