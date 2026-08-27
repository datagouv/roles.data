import json
import unicodedata
from os import error
from typing import Literal

from fastapi import HTTPException, status

from src.repositories.admin.admin_read_repository import AdminReadRepository


GroupSortBy = Literal["id", "name", "user_count", "created_at", "updated_at"]
UserSortBy = Literal["id", "email", "created_at", "updated_at"]
SortDirection = Literal["asc", "desc"]


def _normalize_text(value: str) -> str:
    return "".join(
        character
        for character in unicodedata.normalize("NFKD", value.casefold())
        if not unicodedata.combining(character)
    )


def _filter_and_sort(records, search, text_field, sort_by, sort_direction):
    search = _normalize_text(search.strip())
    matching_records = [
        record
        for record in records
        if search in str(record["id"]) or search in _normalize_text(record[text_field])
    ]

    def sort_key(record):
        value = record[sort_by]
        if isinstance(value, str):
            value = _normalize_text(value)
        return value, record["id"]

    return sorted(matching_records, key=sort_key, reverse=sort_direction == "desc")


class AdminReadService:
    """
    Service class for admin operations, providing methods to interact with the AdminRepository.

    Should only be called from the admin interface!

    Note on architecture :
    - admin operation are few and very sensitive
    - they should never be exposed to the API
    - thus it is preferrable to centralize them in a single service class rather that DDD driven architecture
    - Security is more important than clean architecture here
    """

    def __init__(self, admin_read_repository: AdminReadRepository):
        self.admin_read_repository = admin_read_repository

    async def get_logs(
        self,
        group_id: int | None = None,
        user_id: int | None = None,
        service_provider_id: int | None = None,
    ):
        log_records = await self.admin_read_repository.read_logs(
            group_id, user_id, service_provider_id
        )

        logs = [dict(log) for log in log_records]
        for log in logs:
            if log["new_values"]:
                try:
                    log["parsed_values"] = json.loads(log["new_values"])
                except (json.JSONDecodeError, TypeError):
                    log["parsed_values"] = {error: "Invalid JSON"}
            else:
                log["parsed_values"] = None

        return logs

    async def get_groups(
        self,
        search: str = "",
        sort_by: GroupSortBy = "id",
        sort_direction: SortDirection = "asc",
    ):
        groups = await self.admin_read_repository.read_groups()
        return _filter_and_sort(groups, search, "name", sort_by, sort_direction)

    async def get_group_details(self, group_id: int, include_logs: bool = True):
        matching_groups = await self.admin_read_repository.read_groups([group_id])

        if len(matching_groups) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {group_id} not found",
            )

        group_details = matching_groups[0]
        users = await self.admin_read_repository.read_group_users(group_id)
        scopes = await self.admin_read_repository.read_group_scopes(group_id)
        logs = await self.get_logs(group_id=group_id) if include_logs else []

        return {
            "details": group_details,
            "users": users,
            "scopes": scopes,
            "logs": logs,
        }

    async def get_users(
        self,
        search: str = "",
        sort_by: UserSortBy = "id",
        sort_direction: SortDirection = "asc",
    ):
        records = await self.admin_read_repository.read_users()
        users = [
            dict(user)
            for user in _filter_and_sort(
                records, search, "email", sort_by, sort_direction
            )
        ]
        user_ids = [user["id"] for user in users]
        groups_by_user_id = await self.admin_read_repository.read_user_groups_by_ids(
            user_ids
        )

        for user in users:
            user["groups"] = groups_by_user_id.get(user["id"], [])

        return users

    async def get_user_details(self, user_id: int, include_logs: bool = True):
        user = await self.admin_read_repository.read_user_by_id(user_id)
        groups = await self.admin_read_repository.read_user_groups(user_id)
        logs = await self.get_logs(user_id=user_id) if include_logs else []

        return {
            "user": user,
            "groups": groups,
            "logs": logs,
        }

    async def get_service_providers(self):
        return await self.admin_read_repository.read_service_providers()

    async def get_service_provider_details(self, service_provider_id: int):
        service_providers = await self.get_service_providers()
        return next(
            service_provider
            for service_provider in service_providers
            if service_provider["id"] == service_provider_id
        )

    async def get_service_accounts_and_logs(self, service_provider_id: int):
        logs = await self.get_logs(service_provider_id=service_provider_id)
        service_accounts = await self.admin_read_repository.read_service_accounts(
            service_provider_id=service_provider_id
        )
        return {
            "service_provider_id": service_provider_id,
            "service_accounts": service_accounts,
            "logs": logs,
        }
