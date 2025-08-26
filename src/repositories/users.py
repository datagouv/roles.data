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

    async def get_by_emails(self, emails: list[str]) -> list[UserResponse]:
        """
        Get users by multiple email addresses
        """
        if not emails:
            return []

        async with self.db_session.transaction():
            placeholders = ",".join([f":email_{i}" for i in range(len(emails))])
            query = f"""
                SELECT U.id, U.email, U.is_verified FROM users as U
                WHERE U.email IN ({placeholders})
                """
            return await self.db_session.fetch_all(
                query, {f"email_{i}": email.lower() for i, email in enumerate(emails)}
            )

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

    async def get_all_by_group_ids(
        self, group_ids: list[int]
    ) -> dict[int, list[UserWithRoleResponse]]:
        """
        Retrieve all users for multiple group IDs in a single query
        Returns a dictionary mapping group_id -> list of users
        """
        if len(group_ids) == 0:
            return {}

        async with self.db_session.transaction():
            placeholders = ",".join([f":group_id_{i}" for i in range(len(group_ids))])
            query = f"""
                SELECT U.id, U.email, U.is_verified, U.created_at, R.role_name, R.id as role_id, R.is_admin, TUR.group_id
                FROM users as U
                INNER JOIN group_user_relations as TUR ON TUR.user_id = U.id
                INNER JOIN roles as R ON TUR.role_id = R.id
                WHERE TUR.group_id IN ({placeholders})
                ORDER BY TUR.group_id, R.id ASC, U.id ASC
                """

            values = {f"group_id_{i}": group_id for i, group_id in enumerate(group_ids)}
            rows = await self.db_session.fetch_all(query, values)

            # Group users by group_id
            result = {group_id: [] for group_id in group_ids}
            for row in rows:
                row_dict = dict(row)
                group_id = row_dict["group_id"]
                user_data = {k: v for k, v in row_dict.items() if k != "group_id"}
                result[group_id].append(UserWithRoleResponse(**user_data))

            return result

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

    async def create_many(self, users: list[UserCreate]) -> list[UserResponse]:
        """
        Create multiple users in a single query with RETURNING clause
        """
        if not users:
            return []

        async with self.db_session.transaction():
            values_placeholders = []
            query_values = {}

            for i, user in enumerate(users):
                values_placeholders.append(f"(:email_{i}, :is_verified_{i})")
                query_values[f"email_{i}"] = user.email.lower()
                query_values[f"is_verified_{i}"] = False

            values_clause = ", ".join(values_placeholders)
            query = f"INSERT INTO users (email, is_verified) VALUES {values_clause} RETURNING *"

            created_users = await self.db_session.fetch_all(query, query_values)

            if created_users:
                log_entries = []
                for user_response in created_users:
                    log_entries.append(
                        (
                            user_response["id"],
                            f'{{"email": "{user_response["email"]}"}}',
                        )
                    )

                await self.logs_service.save_many(
                    action_type=LOG_ACTIONS.CREATE_USER,
                    resource_type=LOG_RESOURCE_TYPES.USER,
                    db_session=self.db_session,
                    resource_values=log_entries,
                )

            return created_users
