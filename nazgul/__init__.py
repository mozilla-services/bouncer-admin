import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

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

    from . import api, mysql_model, xmlrenderer

    app.config["MAX_CONTENT_LENGTH"] = 500 * 1024
    app.register_blueprint(api.bp)
    app.register_blueprint(api.hb)

    return app
