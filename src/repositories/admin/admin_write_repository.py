# ------- REPOSITORY FILE -------
from fastapi import HTTPException, status
from pydantic import EmailStr

from src.config import settings
from src.model import ServiceProviderResponse


class AdminWriteRepository:
    """
    Repository for admin-related WRITE operations.
    Does not expect a service account or service provider ID, as it is used for admin operations

    Should only be called from the web interface !
    """

    def __init__(self, db_session, admin_email: EmailStr):
        self.db_session = db_session
        self.admin_email = admin_email

        # extra safety check. All Admin Repositories should never be instantiated without an admin email
        if not self.admin_email or self.admin_email not in settings.SUPER_ADMIN_EMAILS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not authorized to perform admin operations.",
            )

    async def create_service_account(
        self,
        client_id: str,
        service_provider_id: int,
        hashed_password: str | None = None,
    ) -> None:
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

    async def update_service_account(
        self,
        service_provider_id: int,
        service_account_id: int,
        is_active: bool | None = None,
        new_hashed_password: str | None = None,
    ) -> None:
        async with self.db_session.transaction():
            set = []
            values: dict[str, int | str] = {
                "service_account_id": service_account_id,
                "service_provider_id": service_provider_id,
            }

            if is_active is not None:
                set.append("is_active = :is_active")
                values["is_active"] = is_active

            if new_hashed_password is not None:
                set.append("hashed_password = :hashed_password")
                values["hashed_password"] = new_hashed_password

            await self.db_session.execute(
                f"""
                    UPDATE service_accounts
                    SET {", ".join(set)}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = :service_account_id AND service_provider_id = :service_provider_id
                    """,
                values,
            )

    async def set_admin(
        self,
        group_id: int,
        user_id: int,
    ) -> None:
        async with self.db_session.transaction():
            await self.db_session.execute(
                """
                    UPDATE group_user_relations
                    SET role_id = 1
                    WHERE group_id = :group_id AND user_id = :user_id
                    """,
                values={
                    "group_id": group_id,
                    "user_id": user_id,
                },
            )

    async def create_service_provider(
        self, name: str, url: str, proconnect_client_id: str | None = None
    ) -> ServiceProviderResponse:
        async with self.db_session.transaction():
            query = """
                INSERT INTO service_providers (name, url, proconnect_client_id, created_at, updated_at)
                VALUES (:name, :url, :proconnect_client_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING *
            """
            values = {
                "name": name,
                "url": url,
                "proconnect_client_id": proconnect_client_id,
            }
            return await self.db_session.fetch_one(query, values)

    async def update_service_provider(
        self, id: int, name: str, url: str, proconnect_client_id: str | None = None
    ) -> ServiceProviderResponse:
        async with self.db_session.transaction():
            query = """
                UPDATE service_providers
                SET name=:name, url=:url, proconnect_client_id=:proconnect_client_id, updated_at= CURRENT_TIMESTAMP
                WHERE service_providers.id = :id
                RETURNING *
            """
            values = {
                "id": id,
                "name": name,
                "url": url,
                "proconnect_client_id": proconnect_client_id,
            }
            return await self.db_session.fetch_one(query, values)

    async def delete_group(self, group_id: int) -> None:
        """
        Delete a group and all its related data.
        This will cascade to remove users, scopes, and other relations.
        """
        async with self.db_session.transaction():
            # Delete group_user_relations first (foreign key constraint)
            await self.db_session.execute(
                "DELETE FROM group_user_relations WHERE group_id = :group_id",
                {"group_id": group_id},
            )

            # Delete group_service_provider_relations
            await self.db_session.execute(
                "DELETE FROM group_service_provider_relations WHERE group_id = :group_id",
                {"group_id": group_id},
            )

            # Delete the group itself
            await self.db_session.execute(
                "DELETE FROM groups WHERE id = :group_id", {"group_id": group_id}
            )
