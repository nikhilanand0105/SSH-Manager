from tasks.celery import app


@app.task
def revoke_access(ssh_key: bytes, ip_address):
    """
    Celery task for revoking access to the given ip address.

    Args:
        ssh_key:
        ip_address:

    Returns:

    """

    pass
