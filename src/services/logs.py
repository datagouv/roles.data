import json
from typing import Any

from src.model import LOG_ACTIONS, LOG_RESOURCE_TYPES
from src.repositories.logs import LogsRepository


class LogsService:
    def __init__(self, logs_repository: LogsRepository):
        self.logs_repository = logs_repository

    async def save(
        self,
        action_type: LOG_ACTIONS,
        resource_type: LOG_RESOURCE_TYPES,
        resource_id: int | None = None,
        new_values: Any | None = None,
    ) -> None:
        if isinstance(new_values, dict):
            serialized_new_value = json.dumps(new_values, default=str)
        elif isinstance(new_values, str):
            serialized_new_value = new_values
        else:
            serialized_new_value = None

        await self.logs_repository.save(
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            new_values=serialized_new_value,
        )
