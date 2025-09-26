from uuid import UUID

import pytest
from databases import Database
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient

from src.auth.o_auth import decode_access_token

from ..config import settings
from ..database import DatabaseWithSchema, get_db
from ..dependencies.context import RequestContext, get_context
from ..main import app

# Create a test database instance
test_db = Database(settings.DATABASE_URL)

if settings.DB_ENV != "test":
    # Use a different port for the test database
    raise ValueError("DB_ENV must be set to 'test' for testing purposes.")


async def test_db_startup():
    if not test_db.is_connected:
        await test_db.connect()


async def test_db_shutdown():
    await test_db.disconnect()


# Create an override function with the same signature as get_db
async def override_get_db():
    await test_db_startup()

    # Create schema-aware database instance for tests
    schema_test_db = DatabaseWithSchema(test_db, settings.DB_SCHEMA)

    try:
        yield schema_test_db
    finally:
        # We leave the connection open as it's pooled
        pass


def override_decode_access_token():
    """Override decode_access_token to return fake data without JWT validation"""
    return {"service_provider_id": 1, "service_account_id": 1}


def override_get_context(request: Request):
    """Override decode_access_token to return fake data without JWT validation"""
    raw_user_sub = request.query_params.get("acting_user_sub", None)
    valid_acting_user_sub = None
    if raw_user_sub:
        try:
            valid_acting_user_sub = UUID(raw_user_sub, version=4)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid UUID format for user_sub in session: {raw_user_sub}",
            )

    return RequestContext(
        service_provider_id=1,
        service_account_id=1,
        acting_user_sub=valid_acting_user_sub,
        context_type="oauth",
    )


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
    app.dependency_overrides[get_context] = override_get_context
    app.dependency_overrides[decode_access_token] = override_decode_access_token

    # Also override alternative import paths if they exist
    try:
        from src.auth.o_auth import decode_access_token as alt_decode_access_token

        app.dependency_overrides[alt_decode_access_token] = override_decode_access_token
    except ImportError:
        pass

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
