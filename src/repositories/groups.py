# ------- REPOSITORY FILE -------
from src.services.logs import LogsService

from ..model import (
    LOG_ACTIONS,
    LOG_RESOURCE_TYPES,
    GroupCreate,
    GroupResponse,
    GroupWithScopesResponse,
    GroupWithUsersAndScopesResponse,
)


class GroupsRepository:
    def __init__(self, db_session, logs_service: LogsService):
        self.db_session = db_session
        self.logs_service = logs_service

    async def get(
        self, group_id: int, service_provider_id: int
    ) -> GroupWithUsersAndScopesResponse | None:
        async with self.db_session.transaction():
            query = """
            SELECT G.id, G.name, organisations.siret as organisation_siret
            FROM groups as G
            INNER JOIN organisations ON organisations.id = G.orga_id
            INNER JOIN group_service_provider_relations AS GSPR ON GSPR.group_id = G.id AND  GSPR.service_provider_id = :service_provider_id
            WHERE G.id = :id
            """
            return await self.db_session.fetch_one(
                query, {"id": group_id, "service_provider_id": service_provider_id}
            )

    async def get_all(self, service_provider_id: int) -> list[GroupWithScopesResponse]:
        async with self.db_session.transaction():
            query = """
            SELECT G.id, G.name, O.siret as organisation_siret, GSPR.scopes, GSPR.contract_description, GSPR.contract_url
            FROM groups as G
            INNER JOIN organisations AS O ON G.orga_id = O.id
            INNER JOIN group_service_provider_relations AS GSPR ON GSPR.group_id = G.id AND GSPR.service_provider_id = :service_provider_id
            ORDER BY G.id
            """
            return await self.db_session.fetch_all(
                query,
                {
                    "service_provider_id": service_provider_id,
                },
            )

    async def search_by_user(
        self, user_id: int, service_provider_id: int
    ) -> list[GroupWithUsersAndScopesResponse]:
        async with self.db_session.transaction():
            query = """
            SELECT G.id, G.name, O.siret as organisation_siret, GSPR.scopes, GSPR.contract_description, GSPR.contract_url
            FROM groups as G
            INNER JOIN organisations AS O ON G.orga_id = O.id
            INNER JOIN group_user_relations AS GUR ON GUR.group_id = G.id
            INNER JOIN users AS U ON U.id = GUR.user_id
            INNER JOIN group_service_provider_relations AS GSPR ON GSPR.group_id = G.id AND GSPR.service_provider_id = :service_provider_id
            WHERE U.id = :user_id
            ORDER BY G.id
            """
            return await self.db_session.fetch_all(
                query,
                {
                    "user_id": user_id,
                    "service_provider_id": service_provider_id,
                },
            )

    async def create(
        self, group_data: GroupCreate, orga_id: int, service_provider_id: int
    ) -> GroupResponse:
        async with self.db_session.transaction():
            query_create_group = "INSERT INTO groups (name, orga_id) VALUES (:name, :orga_id) RETURNING *"
            new_group = await self.db_session.fetch_one(
                query_create_group, {"name": group_data.name, "orga_id": orga_id}
            )

            query_create_access = "INSERT INTO group_service_provider_relations (service_provider_id, group_id, scopes, contract_description, contract_url) VALUES (:service_provider_id, :group_id, :scopes, :contract_description, :contract_url)"
            await self.db_session.execute(
                query_create_access,
                {
                    "service_provider_id": service_provider_id,
                    "group_id": new_group.id,
                    "scopes": group_data.scopes if group_data.scopes else "",
                    "contract_description": group_data.contract_description
                    if group_data.contract_description
                    else "",
                    "contract_url": str(group_data.contract_url)
                    if group_data.contract_url
                    else "",
                },
            )

            await self.logs_service.save(
                action_type=LOG_ACTIONS.CREATE_GROUP,
                resource_type=LOG_RESOURCE_TYPES.GROUP,
                db_session=self.db_session,
                resource_id=new_group.id,
                new_values={
                    "name": new_group.name,
                    "orga_id": orga_id,
                    "scopes": group_data.scopes if group_data.scopes else "",
                    "contract_description": group_data.contract_description
                    if group_data.contract_description
                    else "",
                    "contract_url": group_data.contract_url
                    if group_data.contract_url
                    else "",
                },
            )

            return new_group

    async def update(self, group_id: int, group_name: str) -> GroupResponse:
        """
        Update group name
        """
        async with self.db_session.transaction():
            query = (
                "UPDATE groups SET name = :group_name WHERE id = :group_id RETURNING *"
            )
            values = {"group_name": group_name, "group_id": group_id}

            await self.logs_service.save(
                action_type=LOG_ACTIONS.UPDATE_GROUP,
                resource_type=LOG_RESOURCE_TYPES.GROUP,
                db_session=self.db_session,
                resource_id=group_id,
                new_values={"name": group_name},
            )

            return await self.db_session.fetch_one(query, values)
