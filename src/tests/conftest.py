import pytest
from fastapi.testclient import TestClient

from ..config import settings
from ..main import app


@pytest.fixture(autouse=True, scope="session")
def setup():
    settings.DB_NAME = settings.DB_NAME_TEST
    settings.DB_PORT = settings.DB_PORT_TEST


@pytest.fixture(scope="session")
def client():
    """
    Fixture to provide a test client for the FastAPI application.
    """
    with TestClient(app) as client:
        yield client
