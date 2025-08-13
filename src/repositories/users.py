# ------- REPOSITORY FILE -------
from pydantic import UUID4

from src.services.logs import LogsService

from ..model import (
    LOG_ACTIONS,
    LOG_RESOURCE_TYPES,
    UserCreate,
    UserResponse,
    UserWithRoleResponse,
)


class UsersRepository:
    def __init__(self, db_session, logs_service: LogsService):
        self.db_session = db_session
        self.logs_service = logs_service

    async def activate(self, user_email: str, user_sub: UUID4) -> UserResponse:
        """
        Mark the user as verified
        """
        async with self.db_session.transaction():
            query = """
            UPDATE users SET sub_pro_connect = :sub_pro_connect, is_verified = TRUE
            WHERE email = :email
            RETURNING *
            """
            values = {"email": user_email.lower(), "sub_pro_connect": user_sub}
            user_response = await self.db_session.fetch_one(query, values)

            await self.logs_service.save(
                action_type=LOG_ACTIONS.VERIFY_USER,
                db_session=self.db_session,
                resource_type=LOG_RESOURCE_TYPES.USER,
                resource_id=user_response["id"],
                new_values=values,
            )
            return user_response

    async def get_sub(self, email: str):
        async with self.db_session.transaction():
            query = """
            SELECT U.sub_pro_connect FROM users as U WHERE U.email = :email
            """
            return await self.db_session.fetch_one(query, {"email": email.lower()})

    async def get_by_email(self, email: str) -> UserResponse:
        async with self.db_session.transaction():
            query = """
            SELECT U.id, U.email, U.is_verified FROM users as U WHERE U.email = :email
            """
            return await self.db_session.fetch_one(query, {"email": email.lower()})

    async def get_by_id(self, user_id: int) -> UserResponse:
        async with self.db_session.transaction():
            query = """
            SELECT U.id, U.email, U.is_verified FROM users as U WHERE U.id = :id
            """
            return await self.db_session.fetch_one(query, {"id": user_id})

    async def get_by_sub(self, user_sub: UUID4) -> UserResponse:
        async with self.db_session.transaction():
            query = """
            SELECT U.id, U.email, U.is_verified FROM users as U WHERE U.sub_pro_connect = :sub_pro_connect
            """
            return await self.db_session.fetch_one(
                query, {"sub_pro_connect": str(user_sub)}
            )

    async def get_all_by_group_id(self, group_id: int) -> list[UserWithRoleResponse]:
        async with self.db_session.transaction():
            query = """
                SELECT U.id, U.email, U.is_verified, U.created_at, R.role_name, R.id as role_id, R.is_admin
                FROM users as U
                INNER JOIN group_user_relations as TUR ON TUR.user_id = U.id
                INNER JOIN roles as R ON TUR.role_id = R.id
                WHERE TUR.group_id = :group_id
                ORDER BY R.id ASC, U.id ASC
                """
            return await self.db_session.fetch_all(query, {"group_id": group_id})

    async def create(self, user: UserCreate) -> UserResponse:
        async with self.db_session.transaction():
            query = "INSERT INTO users (email, is_verified) VALUES (:email, :is_verified) RETURNING *"
            values = {"email": user.email.lower(), "is_verified": False}

            user_response = await self.db_session.fetch_one(query, values)

            await self.logs_service.save(
                action_type=LOG_ACTIONS.CREATE_USER,
                resource_type=LOG_RESOURCE_TYPES.USER,
                db_session=self.db_session,
                resource_id=user_response["id"],
                new_values={
                    "email": user_response["email"],
                },
            )

            return user_response
