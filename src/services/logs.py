import json
from typing import Any

from databases import Database

from src.model import LOG_ACTIONS, LOG_RESOURCE_TYPES
from src.repositories.logs import LogsRepository


class LogsService:
    def __init__(self, logs_repository: LogsRepository):
        self.logs_repository = logs_repository

    def serialize(self, value: Any | None):
        serialized_new_value = None
        if isinstance(value, dict):
            serialized_new_value = json.dumps(value, default=str)
        elif isinstance(value, str):
            serialized_new_value = value

        return serialized_new_value

    async def save(
        self,
        action_type: LOG_ACTIONS,
        resource_type: LOG_RESOURCE_TYPES,
        db_session: Database,
        resource_id: int | None = None,
        new_values: Any | None = None,
    ) -> None:
        """
        Save an audit log entry.

        NB : require a database session to be passed, as it ensure transaction consistency.
        """
        await self.logs_repository.add_entries(
            action_type=action_type,
            db_session=db_session,
            resource_type=resource_type,
            resource_values=[(resource_id, self.serialize(new_values))],
        )

    async def save_many(
        self,
        action_type: LOG_ACTIONS,
        resource_type: LOG_RESOURCE_TYPES,
        db_session: Database,
        resource_values: list[tuple[int | None, Any | None]],
    ) -> None:
        """
        Save a batch of audit logs entry.

        NB : require a database session to be passed, as it ensure transaction consistency.
        """
        for i, resource_value in enumerate(resource_values):
            resource_values[i] = (resource_value[0], self.serialize(resource_value[1]))

        await self.logs_repository.add_entries(
            action_type=action_type,
            db_session=db_session,
            resource_type=resource_type,
            resource_values=resource_values,
        )
