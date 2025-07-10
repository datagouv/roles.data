# ------- REPOSITORY FILE -------


from databases import Database
from fastapi import HTTPException, status
from pydantic import EmailStr

from config import settings


class AdminRepository:
    """
    Repository for admin-related operations.
    Does not expect a service account or service provider ID, as it is used for admin operations

    Should only be called from the web interface !
    """

    def __init__(self, db_session: Database, admin_email: EmailStr):
        self.db_session = db_session
        self.admin_email = admin_email

        if not self.admin_email or self.admin_email not in settings.SUPER_ADMIN_EMAILS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not authorized to perform admin operations.",
            )

    async def read_logs(
        self,
        group_id: int | None = None,
        user_id: int | None = None,
        service_provider_id: int | None = None,
    ) -> list[dict]:
        async with self.db_session.transaction():
            query = """
                SELECT *
                FROM audit_logs as A
                    """

            where_conditions = []
            values = {}

            if group_id is not None:
                where_conditions.append(
                    "A.resource_id = :group_id AND A.resource_type = 'GROUP'"
                )
                values["group_id"] = group_id

            if user_id is not None:
                where_conditions.append(
                    "A.resource_id = :user_id AND A.resource_type = 'USER'"
                )
                values["user_id"] = user_id

            if service_provider_id is not None:
                where_conditions.append("A.service_provider_id = :service_provider_id")
                values["service_provider_id"] = service_provider_id

            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)

            query += " ORDER BY created_at"

            return await self.db_session.fetch_all(
                query,
                values,
            )

    async def read_groups(self, group_ids: list[int] = []) -> list[dict]:
        async with self.db_session.transaction():
            query = """
                SELECT G.*, O.siret AS organisation_siret, O.name AS organisation_name, COUNT(GUR.user_id) AS user_count
                FROM groups as G
                INNER JOIN organisations AS O ON O.id = G.orga_id
                INNER JOIN group_user_relations AS GUR ON GUR.group_id = G.id
            """
            where_conditions = []
            values = {}

            if len(group_ids) > 0:
                # Create individual parameter placeholders
                placeholders = ", ".join(
                    [f":group_id_{i}" for i in range(len(group_ids))]
                )
                where_conditions.append(f"G.id IN ({placeholders})")

                # Add individual parameters
                for i, group_id in enumerate(group_ids):
                    values[f"group_id_{i}"] = group_id

            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)

            query += " GROUP BY G.id, O.siret, O.name ORDER BY id"
            return await self.db_session.fetch_all(query, values)

    async def read_group_users(self, group_id: int) -> list[dict]:
        async with self.db_session.transaction():
            query = """
                SELECT U.id, U.email, R.role_name as role, GUR.created_at
                FROM group_user_relations AS GUR
                INNER JOIN users as U ON U.id = GUR.user_id
                INNER JOIN roles AS R ON R.id = GUR.role_id
                WHERE GUR.group_id = :group_id
            """
            return await self.db_session.fetch_all(query, values={"group_id": group_id})

    async def read_group_scopes(self, group_id: int) -> list[dict]:
        async with self.db_session.transaction():
            query = """
                SELECT GSR.*, SP.name AS service_provider_name
                FROM group_service_provider_relations AS GSR
                INNER JOIN service_providers AS SP ON SP.id = GSR.service_provider_id
                WHERE GSR.group_id = :group_id
            """
            return await self.db_session.fetch_all(query, values={"group_id": group_id})

    async def read_service_providers(self) -> list[dict]:
        async with self.db_session.transaction():
            query = """
                SELECT *
                FROM service_providers
                ORDER BY id
            """
            return await self.db_session.fetch_all(query)

    async def read_service_accounts(self, service_provider_id: int) -> list[dict]:
        async with self.db_session.transaction():
            query = """
                SELECT *
                FROM service_accounts
                WHERE service_provider_id = :service_provider_id
                ORDER BY id
            """
            return await self.db_session.fetch_all(
                query, values={"service_provider_id": service_provider_id}
            )

    async def read_users(self) -> list[dict]:
        async with self.db_session.transaction():
            query = """
                SELECT *
                FROM users AS U
            """
            return await self.db_session.fetch_all(query, {})

    async def read_user_groups(self, user_id: int) -> list[dict]:
        async with self.db_session.transaction():
            query = """
                SELECT G.name, G.id, R.role_name as role, GUR.created_at
                FROM group_user_relations AS GUR
                INNER JOIN groups as G ON G.id = GUR.group_id
                INNER JOIN roles AS R ON R.id = GUR.role_id
                WHERE GUR.user_id = :user_id
            """
            return await self.db_session.fetch_all(query, values={"user_id": user_id})
