# ------- REPOSITORY FILE -------
from ..models import RoleResponse


class RolesRepository:
    def __init__(self, db_session):
        self.db_session = db_session

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
