import os
import tempfile

import pytest

import sys, os
from nazgul import create_test_app


@pytest.fixture
def client():
    app = create_test_app()
    db_fd, app.config["DATABASE"] = tempfile.mkstemp()
    app.config["TESTING"] = True
    client = app.test_client()

    # with nazgul.app.app_context():
    # nazgul.init_db()

    yield client

    os.close(db_fd)
    os.unlink(app.config["DATABASE"])
