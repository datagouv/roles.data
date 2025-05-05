import pytest
from fastapi.testclient import TestClient

from ..config import settings
from ..main import app


@pytest.fixture(autouse=True, scope="session")
def setup():
    settings.DB_NAME = settings.DB_NAME_TEST
    settings.DB_PORT = settings.DB_PORT_TEST

    settings.DATABASE_PREFLIGHT_QUERY = """
        INSERT INTO d_roles.users (email, sub_pro_connect, is_email_confirmed)
        VALUES ('user@yopmail.com', '', false) ON CONFLICT DO NOTHING;
    """


@pytest.fixture(scope="session")
def client():
    """
    Fixture to provide a test client for the FastAPI application.
    """
    with TestClient(app) as client:
        yield client
