from typing import AsyncGenerator

import databases

from src.config import settings


# Optimized database wrapper that sets schema once per transaction
class DatabaseWithSchema:
    def __init__(self, db, schema):
        self.db = db
        self.schema = schema

    async def execute(self, query, *args, **kwargs):
        await self._ensure_schema_set()
        return await self.db.execute(query, *args, **kwargs)

    async def fetch_one(self, query, *args, **kwargs):
        await self._ensure_schema_set()
        return await self.db.fetch_one(query, *args, **kwargs)

    async def fetch_all(self, query, *args, **kwargs):
        await self._ensure_schema_set()
        return await self.db.fetch_all(query, *args, **kwargs)

    async def _ensure_schema_set(self):
        # For now, set schema on each operation but this could be optimized further
        # by tracking transaction state
        await self.db.execute(f"SET search_path TO {self.schema}")

    def transaction(self, **kwargs):
        return self.db.transaction(**kwargs)

    # Pass through other attributes
    def __getattr__(self, name):
        return getattr(self.db, name)


# Create database instance with optimized connection pooling
database = databases.Database(
    settings.DATABASE_URL,
    min_size=5,  # Keep minimum 5 connections open
    max_size=20,  # Allow up to 20 concurrent connections
    max_inactive_connection_lifetime=60,  # Close idle connections after 1 minute
)


async def startup():
    if not database.is_connected:
        await database.connect()


async def shutdown():
    if database.is_connected:
        await database.disconnect()


# Dependency to get DB connection
async def get_db() -> AsyncGenerator[DatabaseWithSchema, None]:
    await startup()

    # Create schema-aware database instance
    schema_database = DatabaseWithSchema(database, settings.DB_SCHEMA)

    try:
        yield schema_database
    finally:
        # We leave the connection open as it's pooled
        pass
