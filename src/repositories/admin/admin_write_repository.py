# ------- REPOSITORY FILE -------
from databases import Database
from fastapi import HTTPException, status
from pydantic import EmailStr

from src.config import settings


class AdminWriteRepository:
    """
    Repository for admin-related WRITE operations.
    Does not expect a service account or service provider ID, as it is used for admin operations

    Should only be called from the web interface !
    """

    def __init__(self, db_session: Database, admin_email: EmailStr):
        self.db_session = db_session
        self.admin_email = admin_email

        # extra safety check. All Admin Repositories should never be instantiated without an admin email
        if not self.admin_email or self.admin_email not in settings.SUPER_ADMIN_EMAILS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not authorized to perform admin operations.",
            )

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
                    SET {', '.join(set)}, updated_at = CURRENT_TIMESTAMP
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
