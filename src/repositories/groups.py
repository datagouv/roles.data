# ------- REPOSITORY FILE -------
from ..models import GroupCreate, GroupResponse, GroupWithUsersResponse


class GroupsRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_rights_on_groups(self, group_id: int, service_provider_id: int):
        async with self.db_session.transaction():
            query = """
            SELECT G.id, GSPR.scopes, G.name
            FROM group as G
            INNER JOIN group_service_provider_relations as GSPR ON GSPR.group_id = G.id AND GSPR.service_provider_id = :service_provider_id
            WHERE G.id = :id
            """
            return await self.db_session.fetch_one(
                query, {"id": group_id, "service_provider_id": service_provider_id}
            )

    async def get_group_by_id(
        self, group_id: int, service_provider_id: int
    ) -> GroupWithUsersResponse | None:
        async with self.db_session.transaction():
            query = """
            SELECT G.id, G.name, organisations.siren as organisation_siren
            FROM groups as G
            INNER JOIN organisations ON organisations.id = G.orga_id
            INNER JOIN group_service_provider_relations AS GSPR ON GSPR.group_id = G.id AND  GSPR.service_provider_id = :service_provider_id
            WHERE G.id = :id
            """
            return await self.db_session.fetch_one(
                query, {"id": group_id, "service_provider_id": service_provider_id}
            )

    async def list_groups(self, service_provider_id: int) -> list[GroupResponse]:
        async with self.db_session.transaction():
            query = """
            SELECT G.id, G.name, O.siren as organisation_siren
            FROM groups as G
            INNER JOIN organisations AS O ON G.orga_id = O.id
            INNER JOIN group_service_provider_relations AS GSPR ON GSPR.group_id = G.id AND GSPR.service_provider_id = :service_provider_id
            """
            return await self.db_session.fetch_all(
                query,
                {
                    "service_provider_id": service_provider_id,
                },
            )

    async def create_group(
        self, group_data: GroupCreate, orga_id: int, service_provider_id: int
    ) -> GroupResponse:
        async with self.db_session.transaction():
            query_create_group = "INSERT INTO groups (name, orga_id) VALUES (:name, :orga_id) RETURNING *"
            new_group = await self.db_session.fetch_one(
                query_create_group, {"name": group_data.name, "orga_id": orga_id}
            )

            query_create_access = "INSERT INTO group_service_provider_relations (service_provider_id, group_id, scopes) VALUES (:service_provider_id, :group_id, :scopes)"
            await self.db_session.execute(
                query_create_access,
                {
                    "service_provider_id": service_provider_id,
                    "group_id": new_group.id,
                    "scopes": "",
                },
            )
            return new_group

    async def update_group(self, group_id: int, group_name: str) -> GroupResponse:
        async with self.db_session.transaction():
            query = (
                "UPDATE groups SET name = :group_name WHERE id = :group_id RETURNING *"
            )
            values = {"group_name": group_name, "group_id": group_id}
            return await self.db_session.fetch_one(query, values)

    async def add_user_to_group(
        self, group_id: int, user_id: int, role_id: int
    ) -> None:
        async with self.db_session.transaction():
            query = "INSERT INTO group_user_relations (group_id, user_id, role_id) VALUES (:group_id, :user_id, :role_id)"
            values = {
                "group_id": group_id,
                "user_id": user_id,
                "role_id": role_id,
            }
            await self.db_session.execute(query, values)

    async def remove_user_from_group(self, group_id: int, user_id: int) -> None:
        async with self.db_session.transaction():
            query = "DELETE FROM group_user_relations WHERE group_id = :group_id AND user_id = :user_id"
            values = {"group_id": group_id, "user_id": user_id}
            await self.db_session.execute(query, values)

    async def update_user_role_in_group(
        self, group_id: int, user_id: int, role_id: int
    ) -> None:
        async with self.db_session.transaction():
            query = "UPDATE group_user_relations SET role_id = :role_id WHERE group_id = :group_id AND user_id = :user_id"
            values = {"role_id": role_id, "group_id": group_id, "user_id": user_id}
            await self.db_session.execute(query, values)
