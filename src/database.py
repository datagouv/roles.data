from typing import AsyncGenerator

import databases

from .config import settings

# Create database instance
database = databases.Database(settings.DATABASE_URL)


async def startup():
    if not database.is_connected:
        await database.connect()
        await database.execute(
            f"ALTER ROLE current_user SET search_path TO {settings.DB_SCHEMA}"
        )


async def shutdown():
    if database.is_connected:
        await database.disconnect()


# Dependency to get DB connection
async def get_db() -> AsyncGenerator[databases.Database, None]:
    await startup()
    try:
        yield database
    finally:
        # We leave the connection open as it's pooled
        pass
