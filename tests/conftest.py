import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from pamps.app import app
from pamps.db import engine
from pamps.cli import create_user

os.environ["PAMPS_DB__uri"] = "postgresql://postgres:postgres@db:5432/pamps_test"


@pytest.fixture(scope="function")
def api_client():
    return TestClient(app)


@pytest.fixture(scope="function")
def session():
    with Session(engine) as session:
        return session


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
