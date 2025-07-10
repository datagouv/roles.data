# ------- REPOSITORY FILE -------
from src.model import LOG_ACTIONS, LOG_RESOURCE_TYPES, ScopeResponse
from src.services.logs import LogsService


class ScopesRepository:
    def __init__(self, db_session, logs_service: LogsService):
        self.db_session = db_session
        self.logs_service = logs_service

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
            response = await self.db_session.fetch_one(
                query,
                {
                    "service_provider_id": service_provider_id,
                    "group_id": group_id,
                    "scopes": scopes,
                    "contract": contract,
                },
            )

            await self.logs_service.save(
                action_type=LOG_ACTIONS.UPDATE_GROUP_SERVICE_PROVIDER_RELATION,
                resource_type=LOG_RESOURCE_TYPES.GROUP_SERVICE_PROVIDER_RELATION,
                db_session=self.db_session,
                resource_id=response["id"],
                new_values={"scopes": scopes, "contract": contract},
            )

            return response
