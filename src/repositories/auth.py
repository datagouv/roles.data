# ------- REPOSITORY FILE -------


from src.models import ServiceAccountResponse


class AuthRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_service_account(
        self, service_account_name: str
    ) -> ServiceAccountResponse:
        async with self.db_session.transaction():
            query = """
        SELECT SA.*
        FROM service_accounts as SA
        WHERE SA.name = :service_account_name
        """
            return await self.db_session.fetch_one(
                query, {"service_account_name": service_account_name}
            )
