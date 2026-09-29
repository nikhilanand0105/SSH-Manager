import sys

from ssh_manager_backend.db.database import init_db
from ssh_manager_backend.db.schema import PrivateKey, PublicKey, Session, User

init_db()
