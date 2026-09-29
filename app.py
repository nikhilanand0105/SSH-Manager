import logging

from flask import Flask, json

from ssh_manager_backend.config import routes
from ssh_manager_backend.db.database import db_session

app = Flask(__name__)

app.register_blueprint(routes.rsa_)
app.register_blueprint(routes.users_)


@app.teardown_appcontext
def shutdown_session(*args) -> None:
    """
    Shuts down database session on application close

    Args:
        *args:

    :return: None
    """

    db_session.remove()


@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps(
        {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    )
    response.content_type = "application/json"
    return response


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(message)s")
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
