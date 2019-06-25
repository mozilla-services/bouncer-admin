import nazgul.api as api
from flask import Flask
import os


if __name__ == "__main__":
    app = Flask(__name__, instance_relative_config=True)
    app.register_blueprint(api.bp)
    app.run(host="0.0.0.0", port=os.environ.get("PORT", 5000))
