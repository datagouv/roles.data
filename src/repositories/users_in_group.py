# ------- REPOSITORY FILE -------
from src.model import (
    LOG_ACTIONS,
    LOG_RESOURCE_TYPES,
)
from src.services.logs import LogsService


class UsersInGroupRepository:
    def __init__(self, db_session, logs_service: LogsService):
        self.db_session = db_session
        self.logs_service = logs_service

    async def add_users(
        self, group_id: int, user_role_pairs: list[tuple[int, int]]
    ) -> None:
        """
        Add users to a group (batch)
        user_role_pairs: list of (user_id, role_id) tuples
        """
        if not user_role_pairs:
            return

        async with self.db_session.transaction():
            # Build single INSERT query for all users
            values_placeholders = []
            query_values = {"group_id": group_id}
            log_entries = []

            for i, (user_id, role_id) in enumerate(user_role_pairs):
                values_placeholders.append(f"(:group_id, :user_id_{i}, :role_id_{i})")
                query_values[f"user_id_{i}"] = user_id
                query_values[f"role_id_{i}"] = role_id

                # Collect log entries
                log_entries.append(
                    (group_id, f'{{"user_id": {user_id}, "role_id": {role_id}}}')
                )

            values_clause = ", ".join(values_placeholders)
            query = f"INSERT INTO group_user_relations (group_id, user_id, role_id) VALUES {values_clause}"

            await self.db_session.execute(query, query_values)

            # Batch insert logs
            if log_entries:
                await self.logs_service.save_many(
                    action_type=LOG_ACTIONS.ADD_USER_TO_GROUP,
                    resource_type=LOG_RESOURCE_TYPES.GROUP,
                    db_session=self.db_session,
                    resource_values=log_entries,
                )

    async def remove_user(self, group_id: int, user_id: int) -> None:
        async with self.db_session.transaction():
            query = "DELETE FROM group_user_relations WHERE group_id = :group_id AND user_id = :user_id"
            values = {"group_id": group_id, "user_id": user_id}
            await self.db_session.execute(query, values)

            await self.logs_service.save(
                action_type=LOG_ACTIONS.REMOVE_USER_FROM_GROUP,
                resource_type=LOG_RESOURCE_TYPES.GROUP,
                db_session=self.db_session,
                resource_id=group_id,
                new_values={
                    "user_id": user_id,
                },
            )

    async def update_user_role(self, group_id: int, user_id: int, role_id: int) -> None:
        async with self.db_session.transaction():
            query = "UPDATE group_user_relations SET role_id = :role_id WHERE group_id = :group_id AND user_id = :user_id"
            values = {"role_id": role_id, "group_id": group_id, "user_id": user_id}
            await self.db_session.execute(query, values)

            await self.logs_service.save(
                action_type=LOG_ACTIONS.UPDATE_USER_ROLE,
                resource_type=LOG_RESOURCE_TYPES.GROUP,
                db_session=self.db_session,
                resource_id=group_id,
                new_values={
                    "user_id": user_id,
                    "role_id": role_id,
                },
            )
