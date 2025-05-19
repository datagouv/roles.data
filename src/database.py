from typing import AsyncGenerator

import databases

from .config import settings


# wrapper that ensure we always use schema
class DatabaseWithSchema:
    def __init__(self, db, schema):
        self.db = db
        self.schema = schema

    async def execute(self, query, *args, **kwargs):
        await self.db.execute(f"SET search_path TO {self.schema}")
        return await self.db.execute(query, *args, **kwargs)

    async def fetch_one(self, query, *args, **kwargs):
        await self.db.execute(f"SET search_path TO {self.schema}")
        return await self.db.fetch_one(query, *args, **kwargs)

    async def fetch_all(self, query, *args, **kwargs):
        await self.db.execute(f"SET search_path TO {self.schema}")
        return await self.db.fetch_all(query, *args, **kwargs)

    # Add other methods as needed

    # Pass through other attributes
    def __getattr__(self, name):
        return getattr(self.db, name)


# Create database instance
database = databases.Database(settings.DATABASE_URL)


async def startup():
    if not database.is_connected:
        await database.connect()
        # on startup we set the schema
        await database.execute(f"SET search_path TO {settings.DB_SCHEMA}")


async def shutdown():
    if database.is_connected:
        await database.disconnect()


# Dependency to get DB connection
async def get_db() -> AsyncGenerator[DatabaseWithSchema, None]:
    await startup()

    # always ensure the schema is set (for every connections of the pool)
    schema_database = DatabaseWithSchema(database, settings.DB_SCHEMA)

    try:
        yield schema_database
    finally:
        # We leave the connection open as it's pooled
        pass
