import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import MetaData
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from typer.testing import CliRunner

from pamps.db import engine

# This next line ensures tests uses its own database and settings environment
os.environ["FORCE_ENV_FOR_DYNACONF"] = "testing"  # noqa

from pamps import app, db  # noqa
from pamps.cli import cli, create_user
from pamps.config import settings  # noqa


# each test runs on cwd to its temp dir
@pytest.fixture(autouse=True)
def go_to_tmpdir(request):
    # Get the fixture dynamically by its name.
    tmpdir = request.getfixturevalue("tmpdir")
    # ensure local test created packages can be imported
    sys.path.insert(0, str(tmpdir))
    # Chdir only for the duration of the test.
    with tmpdir.as_cwd():
        yield


@pytest.fixture(scope="function", name="app")
def _app():
    return app


@pytest.fixture(scope="function", name="cli")
def _cli():
    return cli


@pytest.fixture(scope="function", name="settings")
def _settings():
    return settings


@pytest.fixture(scope="function")
def api_client():
    return TestClient(app)


def create_api_client_authenticated(username, user_id):
    try:
        create_user(f"{username}@pamps.com", username, username, user_id=user_id)
    except IntegrityError:
        pass

    client = TestClient(app)
    token = client.post(
        "/token",
        data={"username": username, "password": username},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ).json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture(scope="function")
def api_client_user_1():
    return create_api_client_authenticated("user_1", 1)


@pytest.fixture(scope="function")
def api_client_user_2():
    return create_api_client_authenticated("user_2", 2)


@pytest.fixture(scope="function")
def cli_client():
    return CliRunner()


def remove_db(engine):
    metadata = MetaData(bind=engine)
    metadata.reflect()
    metadata.drop_all()


@pytest.fixture(scope="session", autouse=True)
def setup_db(request):
    db.create_db_and_tables(db.engine)
    yield
    request.addfinalizer(lambda: remove_db(db.engine))


@pytest.fixture(scope="function")
def session():
    with Session(engine) as session:
        with session.begin():
            yield session
