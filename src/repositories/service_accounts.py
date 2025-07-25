class ServiceAccountsRepository:
    """Repository for service account database operations."""

    def __init__(self, db_session):
        self.db_session = db_session

    async def get_by_service_provider(self, service_provider_id: int) -> list[dict]:
        """Get all service accounts for a service provider."""
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

    async def create(
        self,
        client_id: str,
        service_provider_id: int,
        hashed_password: str | None = None,
    ) -> None:
        """Create a new service account."""
        async with self.db_session.transaction():
            query = """
            INSERT INTO service_accounts (
                service_provider_id,
                name,
                hashed_password,
                is_active
            )
            VALUES (:service_provider_id, :name, :hashed_password, TRUE)
            """
            values = {
                "name": client_id,
                "service_provider_id": service_provider_id,
                "hashed_password": hashed_password,
            }
            return await self.db_session.execute(query, values)

    async def update(
        self,
        service_provider_id: int,
        service_account_id: int,
        is_active: bool | None = None,
        new_hashed_password: str | None = None,
    ) -> None:
        """Update a service account."""
        async with self.db_session.transaction():
            set_clauses = []
            values: dict[str, int | str] = {
                "service_account_id": service_account_id,
                "service_provider_id": service_provider_id,
            }

            if is_active is not None:
                set_clauses.append("is_active = :is_active")
                values["is_active"] = is_active

            if new_hashed_password is not None:
                set_clauses.append("hashed_password = :hashed_password")
                values["hashed_password"] = new_hashed_password

            await self.db_session.execute(
                f"""
                    UPDATE service_accounts
                    SET {", ".join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = :service_account_id AND service_provider_id = :service_provider_id
                    """,
                values,
            )
