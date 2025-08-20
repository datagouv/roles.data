import pytest
from databases import Database
from fastapi import Depends
from fastapi.testclient import TestClient
from pydantic import UUID4, EmailStr

from src.auth.o_auth import decode_access_token

from ..config import settings
from ..database import DatabaseWithSchema, get_db
from ..dependencies import get_logs_service_o_auth
from ..main import app
from ..repositories.users import UsersRepository
from ..services.ui.activation_service import ActivationService

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


# Test-only route for user activation
async def test_activate_user(
    user_email: EmailStr,
    user_sub: UUID4,
    logs_service=Depends(get_logs_service_o_auth),
    db=Depends(get_db),
):
    """Test-only route for activating users."""
    users_repository = UsersRepository(db, logs_service)
    activation_service = ActivationService(users_repository)
    return await activation_service.activate_user(
        user_sub=user_sub, user_email=user_email
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
    app.dependency_overrides[decode_access_token] = override_decode_access_token

    # Add test-only routes
    app.add_api_route(
        "/users/activate", test_activate_user, methods=["PATCH"], status_code=200
    )

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
