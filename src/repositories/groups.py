# ------- REPOSITORY FILE -------
from ..models import GroupCreate, GroupResponse, GroupWithUsersResponse, Siren


class GroupsRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_group_by_id(self, group_id: int) -> GroupWithUsersResponse | None:
        async with self.db_session.transaction():
            query = """
            SELECT T.id, T.name, organisations.siren as organisation_siren
            FROM groups as T
            INNER JOIN organisations ON organisations.id = T.orga_id
            WHERE T.id = :id
            """
            return await self.db_session.fetch_one(query, {"id": group_id})

    async def create_group(
        self, group_data: GroupCreate, orga_id: int
    ) -> GroupResponse:
        async with self.db_session.transaction():
            query = "INSERT INTO groups (name, orga_id) VALUES (:name, :orga_id) RETURNING *"
            values = {"name": group_data.name, "orga_id": orga_id}
            return await self.db_session.fetch_one(query, values)

    async def list_groups(self, organisation_siren: Siren) -> list[GroupResponse]:
        async with self.db_session.transaction():
            query = """
            SELECT T.id, T.name, O.siren as organisation_siren FROM teams as T INNER JOIN organisations AS O ON T.orga_id = O.id WHERE O.siren = :organisation_siren"
            """
            return await self.db_session.fetch_all(
                query, {"organisation_siren": organisation_siren}
            )

    async def delete_group(self, group_id: int) -> None:
        async with self.db_session.transaction():
            query = "DELETE FROM groups WHERE id = :group_id"
            values = {"group_id": group_id}
            return await self.db_session.execute(query, values)

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
