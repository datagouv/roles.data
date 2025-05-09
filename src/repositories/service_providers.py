from src.models import ServiceProviderResponse


class ServiceProvidersRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_by_id(self, service_provider_id: int) -> ServiceProviderResponse:
        async with self.db_session.transaction():
            query = """
            SELECT SP.id, SP.name
            FROM service_providers as SP
            WHERE SP.id = :service_provider_id
            """
            return await self.db_session.fetch_one(
                query, {"service_provider_id": service_provider_id}
            )

    async def get_all(self) -> list[ServiceProviderResponse]:
        async with self.db_session.transaction():
            query = """
            SELECT SP.id, SP.name
            FROM service_providers as SP
            """
            return await self.db_session.fetch_all(query)
