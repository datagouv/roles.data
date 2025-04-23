from typing import AsyncGenerator

import databases

from .config import settings

# Create database instance
database = databases.Database(settings.DATABASE_URL)  # type: ignore


# Dependency to get DB connection
async def get_db() -> AsyncGenerator[databases.Database, None]:
    if not database.is_connected:
        await database.connect()
    try:
        yield database
    finally:
        # We leave the connection open as it's pooled
        pass


# For use in app startup/shutdown
async def startup():
    await database.connect()


async def shutdown():
    await database.disconnect()
