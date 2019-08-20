import nazgul.api as api
from flask import Flask
import os


if __name__ == "__main__":
    app = Flask(__name__, instance_relative_config=True)
    app.register_blueprint(api.bp)
    app.register_blueprint(api.hb)
    app.url_map.strict_slashes = True
    app.config["MAX_CONTENT_LENGTH"] = 500 * 1024
    app.run(host="0.0.0.0", port=os.environ.get("PORT", 5000))
