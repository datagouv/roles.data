# ------- REPOSITORY FILE -------
from ..models import GroupCreate, GroupResponse, GroupWithUsersResponse, Siren


class GroupsRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_group_by_id(self, group_id: int) -> GroupWithUsersResponse | None:
        async with self.db_session.transaction():
            query = """
            SELECT T.id, T.name, d_roles.organisations.siren as organisation_siren
            FROM d_roles.groups as T
            INNER JOIN d_roles.organisations ON d_roles.organisations.id = T.orga_id
            WHERE T.id = :id
            """
            return await self.db_session.fetch_one(query, {"id": group_id})

    async def create_group(
        self, group_data: GroupCreate, orga_id: int
    ) -> GroupResponse:
        async with self.db_session.transaction():
            query = "INSERT INTO d_roles.groups (name, orga_id) VALUES (:name, :orga_id) RETURNING *"
            values = {"name": group_data.name, "orga_id": orga_id}
            return await self.db_session.fetch_one(query, values)

    async def list_groups(self, organisation_siren: Siren) -> list[GroupResponse]:
        async with self.db_session.transaction():
            query = "SELECT T.id, T.name, d_roles.organisations.siren as organisation_siren FROM d_roles.groups as T INNER JOIN d_roles.organisations ON d_roles.organisations.siren = :organisation_siren"
            return await self.db_session.fetch_all(
                query, {"organisation_siren": organisation_siren}
            )

    async def delete_group(self, group_id: int) -> None:
        async with self.db_session.transaction():
            query = "DELETE FROM d_roles.groups WHERE id = :group_id"
            values = {"group_id": group_id}
            return await self.db_session.execute(query, values)

    async def update_group(self, group_id: int, group_name: str) -> GroupResponse:
        async with self.db_session.transaction():
            query = "UPDATE d_roles.groups SET name = :group_name WHERE id = :group_id RETURNING *"
            values = {"group_name": group_name, "group_id": group_id}
            return await self.db_session.fetch_one(query, values)

    async def add_user_to_group(
        self, group_id: int, user_id: int, is_admin: bool
    ) -> None:
        async with self.db_session.transaction():
            query = "INSERT INTO d_roles.group_user_relations (group_id, user_id, role_id) VALUES (:group_id, :user_id, :role_id)"
            values = {
                "group_id": group_id,
                "user_id": user_id,
                "role_id": 1 if is_admin else 0,
            }
            await self.db_session.execute(query, values)
