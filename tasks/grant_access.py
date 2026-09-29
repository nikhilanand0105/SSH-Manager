import os

import yaml

from ssh_manager_backend.app.models import AccessControlModel, UserModel
from ssh_manager_backend.app.services import AES, utils
from ssh_manager_backend.db import Key, User
from tasks.celery import app


def update_ansible_host_file(username: str, ip_address: str):
    """
    Updates the ansible host file.

    Args:
        username:
        ip_address

    Returns:

    """

    with open("./ansible/inventory", "w") as host_file:
        host_file.write(
            "[host:vars]\n"
            f"ansible_ssh_private_key_file=./ansible/keys/admin_{ip_address}.pem\n\n"
            "[host]\n"
            f"{ip_address}\n"
        )


def create_ssh_key_file(username: str, ssh_key: bytes, ip_address: str):
    """
    Creates the pem file for SSH.

    Args:
        username:
        ssh_key:
        ip_address:

    Returns:

    """

    if not os.path.exists("./ansible/keys"):
        os.mkdir("./ansible/keys")

    with open(f"./ansible/keys/admin_{ip_address}.pem", "w") as ssh_key_file:
        ssh_key_file.write(ssh_key.decode())

    os.system(f"chmod 400 ./ansible/keys/admin_{ip_address}.pem")


def create_user_key_file(username: str):
    """
    Fetches the user's key from db and creates a file with that name.

    Args:
        username:

    Returns:

    """

    user: User = UserModel().get_user(username=username)
    user_key: Key = user.public_key

    public_key: bytes = user_key.public_key

    if not os.path.exists("./ssh_ca"):
        os.mkdir("./ssh_ca")

    with open(f"./ssh_ca/{username}.pub") as public_key_file:
        public_key_file.write(public_key.decode())


def update_ansible_vars(remote_username: str, username: str, ip_address: str):
    """
    Updates the ansible variables.

    Args:
        remote_username:
        username:
        ip_address:

    Returns:

    """

    with open("./ansible/vars/params.yml") as yaml_file:
        params = yaml.load(yaml_file)

    params["remote_user"] = remote_username
    params["ca_name"] = f"admin_{ip_address}"

    with open("./ansible/vars/params.yml", "w") as yaml_file:
        yaml.dump(params, yaml_file)


@app.task
def grant_access(username: str, ssh_key: bytes, ip_address: str, remote_username: str):
    """
    Celery task for granting access to the given ip address.

    Args:
        remote_username:
        username:
        ssh_key:
        ip_address:

    Returns:

    """

    create_ssh_key_file(username=username, ssh_key=ssh_key, ip_address=ip_address)
    update_ansible_host_file(username=username, ip_address=ip_address)
    update_ansible_vars(
        remote_username=remote_username, username=username, ip_address=ip_address
    )
    AccessControlModel().grant_access(username=username, ip_addresses=[ip_address])
