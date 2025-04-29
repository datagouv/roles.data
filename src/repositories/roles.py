# ------- REPOSITORY FILE -------
from ..models import RoleResponse


class RolesRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def create_role(self, role_data) -> RoleResponse:
        async with self.db_session.transaction():
            query = """
            INSERT INTO roles (role_name, is_admin)
            VALUES (:role_name, :is_admin)
            RETURNING *
            """
            values = {
                "role_name": role_data.role_name,
                "is_admin": role_data.is_admin,
            }
            return await self.db_session.fetch_one(query, values)

    async def get_roles_for_group(self, group_id: int) -> list[RoleResponse]:
        async with self.db_session.transaction():
            query = """
            SELECT R.id, R.role_name, R.is_admin
            FROM group_user_relations AS GUR
            INNER JOIN roles AS R ON GUR.role_id = R.id
            WHERE GUR.group_id = :group_id
            """
            return await self.db_session.fetch_all(query, {"group_id": group_id})

    async def get_roles_by_id(self, role_id: int) -> RoleResponse:
        async with self.db_session.transaction():
            query = """
            SELECT R.id, R.role_name, R.is_admin
            FROM roles AS R
            WHERE R.id = :role_id
            """
            return await self.db_session.fetch_one(query, {"role_id": role_id})

    async def get_all(self) -> list[RoleResponse]:
        async with self.db_session.transaction():
            query = """
            SELECT R.id, R.role_name, R.is_admin
            FROM roles AS R
            """
            return await self.db_session.fetch_all(query)
