from uuid import UUID

import pytest
from databases import Database
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient
from pydantic import UUID4, EmailStr

from src.config import settings
from src.database import DatabaseWithSchema, get_db
from src.dependencies.auth.o_auth import decode_access_token
from src.dependencies.auth.pro_connect_resource_server import (
    ALLOWED_PATHS_FOR_NO_EMAIL_PAIRING,
    get_claims_from_proconnect_token,
)
from src.dependencies.context import RequestContext, get_context
from src.main import app
from src.repositories.users_sub import UserSubsRepository
from src.services.user_subs import UserSubsService

# Create bearer scheme for testing
bearer_scheme = HTTPBearer()

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


async def override_get_claims_from_proconnect_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: DatabaseWithSchema = Depends(get_db),
) -> tuple[UUID4, EmailStr, int]:
    """
    Override get_claims_from_proconnect_token for testing.

    Parses test token format: test:<sub>:<email>:<client_id>
    Example: test:00000000-0000-4000-8000-000000000001:user@example.com:test_client_1

    Returns: (proconnect_sub, proconnect_email, service_provider_id)

    Note: Bypasses ProConnect introspection, pair function, and service provider lookup
    for test simplicity. Returns service_provider_id=1 for all test tokens.
    """
    fake_test_token = credentials.credentials

    if fake_test_token.startswith("test:"):
        parts = fake_test_token.split(":")
        try:
            sub = UUID(parts[1])
            user_sub_service = UserSubsService(UserSubsRepository(db))
            email = await user_sub_service.get_email(sub)

            if not email:
                email = parts[2]
                if request.url.path not in ALLOWED_PATHS_FOR_NO_EMAIL_PAIRING:
                    await user_sub_service.pair(email, sub)

            return (sub, email, 1)
        except (ValueError, IndexError) as error:
            print(error)
            pass

    raise Exception("Must provide a valid Bearer header")


def override_get_context(request: Request):
    """Override decode_access_token to return fake data without JWT validation"""
    if request.url.path.startswith("/resource-server/"):
        return RequestContext(
            service_provider_id=1,
            service_account_id=0,
            acting_user_sub=None,
            context_type="resource_server",
        )

    return RequestContext(
        service_provider_id=1,
        service_account_id=1,
        acting_user_sub=None,
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
    app.dependency_overrides[get_claims_from_proconnect_token] = (
        override_get_claims_from_proconnect_token
    )

    # Also override alternative import paths if they exist
    try:
        from dependencies.auth.pro_connect_resource_server import (
            get_claims_from_proconnect_token as alt_get_claims_from_proconnect_token,
        )
        from src.dependencies.auth.o_auth import (
            decode_access_token as alt_decode_access_token,
        )

        app.dependency_overrides[alt_decode_access_token] = override_decode_access_token
        app.dependency_overrides[alt_get_claims_from_proconnect_token] = (
            override_get_claims_from_proconnect_token
        )
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
