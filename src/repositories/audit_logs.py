# ------- REPOSITORY FILE -------

from databases import Database


class AuditLogsRepository:
    """Repository for reading audit logs - separate from logging operations."""

    def __init__(self, db_session: Database):
        self.db_session = db_session

    async def get_logs(
        self,
        group_id: int | None = None,
        user_id: int | None = None,
        service_provider_id: int | None = None,
    ) -> list[dict]:
        """Get audit logs with optional filtering."""
        async with self.db_session.transaction():
            query = """
                SELECT A.*, U.id AS acting_user_id, U.email AS acting_user_email
                FROM audit_logs as A
                LEFT JOIN users as U ON U.sub_pro_connect = A.acting_user_sub
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

            return await self.db_session.fetch_all(query, values)
