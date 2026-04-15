import json
from os import error

from fastapi import HTTPException, status

from src.repositories.admin.admin_read_repository import AdminReadRepository


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

    async def get_groups(self):
        groups = [dict(group) for group in await self.admin_read_repository.read_groups()]
        group_ids = [group["id"] for group in groups]
        admins_by_group_id = await self.admin_read_repository.read_group_admins_by_ids(
            group_ids
        )

        for group in groups:
            group["admins"] = admins_by_group_id.get(group["id"], [])

        return groups

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

    async def get_users(self):
        users = [dict(user) for user in await self.admin_read_repository.read_users()]
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
