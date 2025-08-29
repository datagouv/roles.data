from src.model import ServiceProviderResponse


class ServiceProvidersRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get(self, service_provider_id: int) -> ServiceProviderResponse:
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

    async def find_by_user(self, user_email: str) -> list[ServiceProviderResponse]:
        async with self.db_session.transaction():
            query = """
            SELECT DISTINCT SP.id, SP.name, SP.url
            FROM service_providers as SP
            JOIN group_service_provider_relations as GSPR ON SP.id = GSPR.service_provider_id
            JOIN groups as G ON GSPR.group_id = G.id
            JOIN group_user_relations as GUR ON G.id = GUR.group_id
            JOIN users as U ON GUR.user_id = U.id
            WHERE U.email = :user_email
            ORDER BY SP.id
            """
            return await self.db_session.fetch_all(query, {"user_email": user_email})
