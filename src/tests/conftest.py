import databases
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from ..config import settings
from ..database import get_db
from ..main import app

testDatabase = databases.Database(settings.TEST_DATABASE_URL)

# Create an async-compatible override
async def override_get_db():
    await testDatabase.connect()
    yield testDatabase


@pytest_asyncio.fixture(scope="session")
async def client():
    """
    Provide a AsyncClient that uses the test database session.
    Override the get_db dependency to use the test session.
    """

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        ) as c:
        yield c
    app.dependency_overrides.clear()
