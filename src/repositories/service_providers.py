from src.model import ServiceProviderResponse


class ServiceProvidersRepository:
    """Repository for service provider database operations."""

    def __init__(self, db_session):
        self.db_session = db_session

    async def get_by_id(self, service_provider_id: int) -> ServiceProviderResponse:
        async with self.db_session.transaction():
            query = """
            SELECT SP.id, SP.name, SP.url
            FROM service_providers as SP
            WHERE SP.id = :service_provider_id
            ORDER BY SP.id
            """
            return await self.db_session.fetch_one(
                query, {"service_provider_id": service_provider_id}
            )

    async def get_all(self) -> list[dict]:
        """Get all service providers for admin operations."""
        async with self.db_session.transaction():
            query = """
                SELECT *
                FROM service_providers
                ORDER BY id
            """
            return await self.db_session.fetch_all(query)

    async def create(self, name: str, url: str) -> ServiceProviderResponse:
        """Create a new service provider."""
        async with self.db_session.transaction():
            query = """
                INSERT INTO service_providers (name, url, created_at, updated_at)
                VALUES (:name, :url, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING *
            """
            values = {"name": name, "url": url}
            return await self.db_session.fetch_one(query, values)
