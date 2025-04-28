import databases
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from ..config import settings
from ..database import get_db
from ..main import app

# Create database instance
testDatabase = databases.Database(settings.TEST_DATABASE_URL)


# This fixture connects to the database
@pytest_asyncio.fixture(scope="session")
async def async_db():
    await testDatabase.connect()
    yield testDatabase
    # Uncomment for cleanup
    # await testDatabase.disconnect()


# Convert async fixture to sync fixture
@pytest.fixture(scope="session")
def db(async_db):
    return async_db


# Create an async-compatible override
async def override_get_db():
    yield testDatabase


@pytest.fixture(scope="session")
def client(db):
    """
    Provide a TestClient that uses the test database session.
    Override the get_db dependency to use the test session.
    """

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
