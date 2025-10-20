from src.model import ServiceProviderResponse


class ServiceProvidersRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get(self, service_provider_id: int) -> ServiceProviderResponse:
        async with self.db_session.transaction():
            query = """
            SELECT SP.id, SP.name, SP.url, SP.proconnect_client_id
            FROM service_providers as SP
            WHERE SP.id = :service_provider_id
            ORDER BY SP.id
            """
            return await self.db_session.fetch_one(
                query, {"service_provider_id": service_provider_id}
            )

    async def get_by_proconnect_client_id(
        self, proconnect_client_id: str
    ) -> ServiceProviderResponse | None:
        """
        Lookup service_provider by ProConnect client_id.
        Returns None if no service provider is found with this client_id.
        """
        async with self.db_session.transaction():
            query = """
            SELECT SP.id, SP.name, SP.url, SP.proconnect_client_id
            FROM service_providers as SP
            WHERE SP.proconnect_client_id = :proconnect_client_id
            """
            return await self.db_session.fetch_one(
                query, {"proconnect_client_id": proconnect_client_id}
            )
