import json
from os import error

from fastapi import HTTPException, status

from src.repositories.admin.admin_repository import AdminRepository
from utils.security import generate_random_password, hash_password


class AdminService:
    """
    Service class for admin operations, providing methods to interact with the AdminRepository.

    Should only be called from the web interface !
    """

    def __init__(self, admin_repository: AdminRepository):
        self.admin_repository = admin_repository

    async def get_logs(
        self,
        group_id: int | None = None,
        user_id: int | None = None,
        service_provider_id: int | None = None,
    ):
        log_records = await self.admin_repository.read_logs(
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
        return await self.admin_repository.read_groups()

    async def get_group_details(self, group_id: int):
        matching_groups = await self.admin_repository.read_groups([group_id])

        if len(matching_groups) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {group_id} not found",
            )

        group_details = matching_groups[0]
        users = await self.admin_repository.read_group_users(group_id)
        scopes = await self.admin_repository.read_group_scopes(group_id)
        logs = await self.get_logs(group_id=group_id)

        return {
            "details": group_details,
            "users": users,
            "scopes": scopes,
            "logs": logs,
        }

    async def get_users(self):
        return await self.admin_repository.read_users()

    async def get_user_details(self, user_id: int):
        groups = await self.admin_repository.read_user_groups(user_id)
        logs = await self.get_logs(user_id=user_id)

        return {
            "groups": groups,
            "logs": logs,
        }

    async def get_service_providers(self):
        return await self.admin_repository.read_service_providers()

    async def get_service_provider_details(self, service_provider_id: int):
        logs = await self.get_logs(service_provider_id=service_provider_id)
        service_accounts = await self.admin_repository.read_service_accounts(
            service_provider_id=service_provider_id
        )
        return {
            "service_provider_id": service_provider_id,
            "service_accounts": service_accounts,
            "logs": logs,
        }

    async def update_service_account(
        self,
        service_provider_id: int,
        service_account_id: int,
        action: str,
    ) -> str | None:
        if action == "activate":
            await self.admin_repository.update_service_account(
                service_provider_id, service_account_id, is_active=True
            )
        elif action == "deactivate":
            await self.admin_repository.update_service_account(
                service_provider_id, service_account_id, is_active=False
            )
        elif action == "reset_secret":
            new_password = generate_random_password()
            new_hashed_password = hash_password(new_password)
            await self.admin_repository.update_service_account(
                service_provider_id,
                service_account_id,
                new_hashed_password=new_hashed_password,
            )
            return new_password
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {action}",
            )
