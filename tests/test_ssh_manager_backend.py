from ssh_manager_backend import __version__
from ssh_manager_backend.db.database import db_session

from ssh_manager_backend.db.schema import (  # AccessControl,; Key,; KeyMapping,
    Session,
    User,
)


def test_version():
    assert __version__ == "0.1.0"


def db_cleanup():
    session = db_session()
    session.query(Session).delete()
    # session.query(AccessControl).delete()
    # session.query(KeyMapping).delete()
    # session.query(Key).delete()
    session.query(User).delete()
    session.commit()
    db_session.remove()
