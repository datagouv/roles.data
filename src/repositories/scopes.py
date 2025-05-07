# ------- REPOSITORY FILE -------


class ScopesRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get(self, service_provider_id: int, group_id: int):
        async with self.db_session.transaction():
            query = """
            SELECT *
            FROM scopes
            WHERE service_provider_id = :service_provider_id AND group_id = :group_id
            """
            return await self.db_session.fetch_one(
                query,
                {"service_provider_id": service_provider_id, "group_id": group_id},
            )

    async def create(self, service_provider_id: int, group_id: int, scopes: str):
        async with self.db_session.transaction():
            query = """
            INSERT INTO scopes (service_provider_id, group_id, scopes)
            VALUES (:service_provider_id, :group_id, :scopes)
            RETURNING *
            """
            return await self.db_session.fetch_one(
                query,
                {
                    "service_provider_id": service_provider_id,
                    "group_id": group_id,
                    "scopes": scopes,
                },
            )

    async def update(self, service_provider_id: int, group_id: int, scopes: str):
        async with self.db_session.transaction():
            query = """
            UPDATE scopes
            SET scopes = :scopes
            WHERE service_provider_id = :service_provider_id AND group_id = :group_id
            RETURNING *
            """
            return await self.db_session.fetch_one(
                query,
                {
                    "service_provider_id": service_provider_id,
                    "group_id": group_id,
                    "scopes": scopes,
                },
            )
