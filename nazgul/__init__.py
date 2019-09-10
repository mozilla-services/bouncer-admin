import json
import os

from flask import Flask


def run_server():
    app = create_app()
    app.run(host="0.0.0.0", port=os.environ.get("PORT", 8000))


def create_test_app(test_config=None):
    app = create_app()
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
        app.config.from_mapping(SECRET_KEY="dev")

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    from . import api

    app.register_blueprint(api.bp)
    app.register_blueprint(api.hb)

    app.url_map.strict_slashes = True

    app.config["MAX_CONTENT_LENGTH"] = 500 * 1024

    app.config["DATABASE_URL"] = os.environ.get("DATABASE_URL", "127.0.0.1")
    app.config["DB_USER"] = os.environ.get("DB_USER", "root")
    app.config["DB_PASS"] = os.environ.get("DB_PASS", "")

    app.config["AUTH_USERS"] = os.environ.get("AUTH_USERS", "{}")

    return app
