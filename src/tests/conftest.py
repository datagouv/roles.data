import pytest
from databases import Database
from fastapi.testclient import TestClient

from ..auth.o_auth import decode_access_token
from ..config import settings
from ..database import DatabaseWithSchema, get_db
from ..main import app

# Create a test database instance
test_db = Database(settings.DATABASE_URL)

if settings.DB_ENV != "test":
    # Use a different port for the test database
    raise ValueError("DB_ENV must be set to 'test' for testing purposes.")


async def test_db_startup():
    if not test_db.is_connected:
        await test_db.connect()
        await test_db.execute(f"SET search_path TO {settings.DB_SCHEMA}")


async def test_db_shutdown():
    await test_db.disconnect()


# Create an override function with the same signature as get_db
async def override_get_db():
    await test_db_startup()

    # always ensure the schema is set (for every connections of the pool)
    schema_test_db = DatabaseWithSchema(test_db, settings.DB_SCHEMA)

    try:
        yield schema_test_db
    finally:
        # We leave the connection open as it's pooled
        pass


def override_decode_access_token():
    return {"service_provider_id": 1, "service_account_id": 1}


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
