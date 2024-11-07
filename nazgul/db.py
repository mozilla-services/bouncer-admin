from flask import current_app, g

from .mysql_model import MySQLModel


def get_db():
    if "db" not in g:
        g.db = MySQLModel(
            host=current_app.config["DATABASE_URL"],
            user=current_app.config["DB_USER"],
            password=current_app.config["DB_PASS"],
            db=current_app.config["DB_NAME"],
        )
    return g.db
