# ------- REPOSITORY FILE -------


from databases import Database

from src.model import LOG_RESOURCE_TYPES, LogResponse


class AdminRepository:
    """
    Repository for admin-related operations.
    Does not expect a service account or service provider ID, as it is used for admin operations
    """

    def __init__(self, db_session: Database):
        self.db_session = db_session

    async def read_logs(
        self,
        service_account_id: int | None = None,
        service_provider_id: int | None = None,
        resource_type: LOG_RESOURCE_TYPES | None = None,
        resource_id: int | None = None,
    ) -> list[LogResponse]:
        async with self.db_session.transaction():
            query = """
                SELECT *
                FROM audit_logs
                    """

            return await self.db_session.fetch_all(
                query,
                values={},
            )
