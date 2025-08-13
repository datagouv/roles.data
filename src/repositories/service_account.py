# ------- REPOSITORY FILE -------


from src.model import ServiceAccountResponse


class ServiceAccountRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get(self, service_account_name: str) -> ServiceAccountResponse:
        async with self.db_session.transaction():
            query = """
        SELECT SA.*
        FROM service_accounts as SA
        WHERE SA.name = :service_account_name
        """
            return await self.db_session.fetch_one(
                query, {"service_account_name": service_account_name}
            )
