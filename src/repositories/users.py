# ------- REPOSITORY FILE -------
from pydantic import UUID4

from src.model import (
    LOG_ACTIONS,
    LOG_RESOURCE_TYPES,
    RoleResponse,
    UserCreate,
    UserResponse,
    UserWithRoleResponse,
)
from src.services.logs import LogsService


class UsersRepository:
    """
    This repository handles the user

    It DOES not access the sub
    """

    def __init__(self, db_session, logs_service: LogsService):
        self.db_session = db_session
        self.logs_service = logs_service

    async def get_by_emails(self, emails: list[str]) -> list[UserResponse]:
        """
        Get users by multiple email addresses
        """
        if not emails:
            return []

        async with self.db_session.transaction():
            placeholders = ",".join([f":email_{i}" for i in range(len(emails))])
            query = f"""
                SELECT U.id, U.email FROM users as U
                WHERE U.email IN ({placeholders})
                """
            return await self.db_session.fetch_all(
                query, {f"email_{i}": email.lower() for i, email in enumerate(emails)}
            )

    async def get_by_id(self, user_id: int) -> UserResponse:
        async with self.db_session.transaction():
            query = """
            SELECT U.id, U.email FROM users as U WHERE U.id = :id
            """
            return await self.db_session.fetch_one(query, {"id": user_id})

    async def get_by_sub(self, user_sub: UUID4) -> UserResponse:
        async with self.db_session.transaction():
            query = """
            SELECT U.id, U.email FROM users as U WHERE U.sub_pro_connect = :sub_pro_connect
            """
            return await self.db_session.fetch_one(
                query, {"sub_pro_connect": str(user_sub)}
            )

    async def get_all_by_group_ids(
        self, group_ids: list[int], limit: int | None = None, offset: int = 0
    ) -> dict[int, list[UserWithRoleResponse]]:
        """
        Retrieve users for multiple group IDs in a single query
        Returns a dictionary mapping group_id -> list of users

        Without a limit, every user of every group is returned. With one, the
        window is applied to each group separately, so every group gets the same
        slice of its own users.
        """
        if len(group_ids) == 0:
            return {}

        async with self.db_session.transaction():
            placeholders = ",".join([f":group_id_{i}" for i in range(len(group_ids))])
            values = {f"group_id_{i}": group_id for i, group_id in enumerate(group_ids)}

            users_query = f"""
                SELECT U.id, U.email, U.created_at, R.role_name, R.id as role_id, R.is_admin, TUR.group_id,
                    ROW_NUMBER() OVER (PARTITION BY TUR.group_id ORDER BY R.id ASC, U.id ASC) AS row_number
                FROM users as U
                INNER JOIN group_user_relations as TUR ON TUR.user_id = U.id
                INNER JOIN roles as R ON TUR.role_id = R.id
                WHERE TUR.group_id IN ({placeholders})
                """

            query = f"""
                SELECT id, email, created_at, role_name, role_id, is_admin, group_id
                FROM ({users_query}) AS numbered_users
                """

            if limit is not None:
                query += (
                    " WHERE row_number > :offset AND row_number <= :offset + :limit"
                )
                values["offset"] = offset
                values["limit"] = limit

            query += " ORDER BY group_id, role_id ASC, id ASC"

            rows = await self.db_session.fetch_all(query, values)

            # Group users by group_id
            result = {group_id: [] for group_id in group_ids}
            for row in rows:
                row_dict = dict(row)
                group_id = row_dict["group_id"]
                user_data = {k: v for k, v in row_dict.items() if k != "group_id"}
                result[group_id].append(UserWithRoleResponse(**user_data))

            return result

    async def get_admins_by_group_ids(
        self, group_ids: list[int], limit: int
    ) -> dict[int, list[UserResponse]]:
        """
        Retrieve the first admins of multiple group IDs in a single query
        Returns a dictionary mapping group_id -> list of admins

        At most `limit` admins are returned per group, the oldest ones first.
        """
        if len(group_ids) == 0:
            return {}

        async with self.db_session.transaction():
            placeholders = ",".join([f":group_id_{i}" for i in range(len(group_ids))])
            values = {f"group_id_{i}": group_id for i, group_id in enumerate(group_ids)}
            values["limit"] = limit

            admins_query = f"""
                SELECT U.id, U.email, TUR.group_id,
                    ROW_NUMBER() OVER (PARTITION BY TUR.group_id ORDER BY U.id ASC) AS row_number
                FROM users as U
                INNER JOIN group_user_relations as TUR ON TUR.user_id = U.id
                INNER JOIN roles as R ON TUR.role_id = R.id
                WHERE TUR.group_id IN ({placeholders}) AND R.is_admin = true
                """

            query = f"""
                SELECT id, email, group_id
                FROM ({admins_query}) AS numbered_admins
                WHERE row_number <= :limit
                ORDER BY group_id, id ASC
                """

            rows = await self.db_session.fetch_all(query, values)

            result = {group_id: [] for group_id in group_ids}
            for row in rows:
                result[row["group_id"]].append(
                    UserResponse(id=row["id"], email=row["email"])
                )

            return result

    async def get_role_in_group(
        self, user_id: int, group_id: int
    ) -> RoleResponse | None:
        """
        Retrieve the role a user holds in a group, or None when they are not in it
        """
        async with self.db_session.transaction():
            query = """
                SELECT R.id, R.role_name, R.is_admin
                FROM group_user_relations as TUR
                INNER JOIN roles as R ON TUR.role_id = R.id
                WHERE TUR.group_id = :group_id AND TUR.user_id = :user_id
                """
            role = await self.db_session.fetch_one(
                query, {"group_id": group_id, "user_id": user_id}
            )
            return RoleResponse(**dict(role)) if role else None

    async def count_by_group_ids(self, group_ids: list[int]) -> dict[int, int]:
        """
        Count the users of multiple group IDs in a single query
        Returns a dictionary mapping group_id -> user count
        """
        if len(group_ids) == 0:
            return {}

        async with self.db_session.transaction():
            placeholders = ",".join([f":group_id_{i}" for i in range(len(group_ids))])
            query = f"""
                SELECT TUR.group_id, COUNT(*) AS user_count
                FROM group_user_relations as TUR
                WHERE TUR.group_id IN ({placeholders})
                GROUP BY TUR.group_id
                """

            values = {f"group_id_{i}": group_id for i, group_id in enumerate(group_ids)}
            rows = await self.db_session.fetch_all(query, values)

            counts = {group_id: 0 for group_id in group_ids}
            for row in rows:
                counts[row["group_id"]] = row["user_count"]

            return counts

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
                values_placeholders.append(f"(:email_{i})")
                query_values[f"email_{i}"] = user.email.lower()

            values_clause = ", ".join(values_placeholders)
            query = f"INSERT INTO users (email) VALUES {values_clause} RETURNING *"

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
