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
        self,
        service_provider_id: int,
        group_id: int,
        scopes: str | None = None,
        contract_description: str | None = None,
        contract_url: str | None = None,
    ):
        async with self.db_session.transaction():
            query = """
            UPDATE group_service_provider_relations
            """

            set = []
            values: dict[str, int | str] = {
                "service_provider_id": service_provider_id,
                "group_id": group_id,
            }

            if scopes is not None:
                set.append("scopes = :scopes")
                values["scopes"] = scopes

            if contract_description is not None:
                set.append("contract_description = :contract_description")
                values["contract_description"] = contract_description

            if contract_url is not None:
                set.append("contract_url = :contract_url")
                values["contract_url"] = contract_url

            query += "SET " + ", ".join(set) + " "
            query += """
            WHERE service_provider_id = :service_provider_id AND group_id = :group_id
            RETURNING *
            """

            if not set:
                raise ValueError(
                    "At least one of scopes, contract_description, or contract_url must be provided."
                )

            response = await self.db_session.fetch_one(
                query,
                values,
            )

            await self.logs_service.save(
                action_type=LOG_ACTIONS.UPDATE_GROUP_SERVICE_PROVIDER_RELATION,
                resource_type=LOG_RESOURCE_TYPES.GROUP_SERVICE_PROVIDER_RELATION,
                db_session=self.db_session,
                resource_id=response["id"],
                new_values={
                    "scopes": scopes,
                    "contract_description": contract_description,
                    "contract_url": contract_url,
                },
            )

            return response
