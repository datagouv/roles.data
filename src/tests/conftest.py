import pytest
from databases import Database
from fastapi.testclient import TestClient

from ..auth import decode_access_token
from ..config import settings
from ..database import get_db
from ..main import app

# Create a test database instance
test_db = Database(settings.DATABASE_TEST_URL)


async def test_db_startup():
    await test_db.connect()
    # Set search path for the entire pool
    await test_db.execute(
        f"ALTER ROLE current_user SET search_path TO {settings.DB_SCHEMA}"
    )


async def test_db_shutdown():
    await test_db.disconnect()


# Create an override function with the same signature as get_db
async def override_get_db():
    await test_db_startup()
    yield test_db


def override_decode_access_token():
    return {"service_provider_id": 1}


@pytest.fixture(scope="session", autouse=True)
def test_override_setup():
    """
    Override the app startup and shutdown events to prevent
    connecting to the production database during tests.
    """

    # Save original handlers
    original_startup_handlers = app.router.on_startup.copy()
    original_shutdown_handlers = app.router.on_shutdown.copy()

    # Clear original handlers
    app.router.on_startup.clear()
    app.router.on_shutdown.clear()

    # Add test-specific handlers if needed
    app.router.on_startup.append(test_db_startup)
    app.router.on_shutdown.append(test_db_shutdown)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[decode_access_token] = override_decode_access_token

    yield

    # Restore original handlers after tests
    app.dependency_overrides.clear()
    app.router.on_startup = original_startup_handlers
    app.router.on_shutdown = original_shutdown_handlers


@pytest.fixture(scope="session")
def client(test_override_setup):
    """Test client using the overridden database connection"""
    with TestClient(app) as client:
        yield client
