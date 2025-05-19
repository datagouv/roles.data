# ------- REPOSITORY FILE -------
from src.models import ScopeResponse


class ScopesRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get(
        self, service_provider_id: int, group_id: int
    ) -> ScopeResponse | None:
        async with self.db_session.transaction():
            query = """
            SELECT *
            FROM group_service_provider_relations as  GSPR
            WHERE GSPR.service_provider_id = :service_provider_id AND GSPR.group_id = :group_id
            """
            return await self.db_session.fetch_one(
                query,
                {"service_provider_id": service_provider_id, "group_id": group_id},
            )

    async def update(
        self, service_provider_id: int, group_id: int, scopes: str, contract: str
    ):
        async with self.db_session.transaction():
            query = """
            UPDATE group_service_provider_relations
            SET scopes = :scopes, contract = :contract
            WHERE service_provider_id = :service_provider_id AND group_id = :group_id
            RETURNING *
            """
            return await self.db_session.fetch_one(
                query,
                {
                    "service_provider_id": service_provider_id,
                    "group_id": group_id,
                    "scopes": scopes,
                    "contract": contract,
                },
            )
