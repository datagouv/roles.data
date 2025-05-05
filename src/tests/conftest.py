import pytest
from fastapi.testclient import TestClient

from ..config import settings
from ..main import app


@pytest.fixture(autouse=True, scope="session")
def setup():
    settings.DB_NAME = settings.DB_NAME_TEST
    settings.DB_PORT = settings.DB_PORT_TEST


@pytest.fixture(autouse=True, scope="session")
async def setup_test_data(db_connection):
    """
    Pre-fill test database with required data
    """
    await db_connection.execute(
        """
        INSERT INTO d_roles.users (email, sub_pro_connect, is_email_confirmed)
        VALUES ('user@yopmail.com', '', false) ON CONFLICT DO NOTHING;
        """
    )

    yield  # This fixture doesn't return anything, just sets up data


@pytest.fixture(scope="session")
def client(setup_test_data):
    """
    Fixture to provide a test client for the FastAPI application.
    """
    with TestClient(app) as client:
        yield client
