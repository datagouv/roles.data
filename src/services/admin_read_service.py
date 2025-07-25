import json

from fastapi import HTTPException, status
from pydantic import EmailStr

from src.config import settings
from src.repositories.audit_logs import AuditLogsRepository
from src.repositories.groups import GroupsRepository
from src.repositories.service_accounts import ServiceAccountsRepository
from src.repositories.service_providers import ServiceProvidersRepository
from src.repositories.users import UsersRepository


class AdminReadService:
    """
    Service class for admin read operations with proper authorization.

    Handles business logic and security for admin operations, reusing existing repositories.
    Should only be called from the web interface!
    """

    def __init__(
        self,
        admin_email: EmailStr,
        audit_logs_repository: AuditLogsRepository,
        groups_repository: GroupsRepository,
        service_providers_repository: ServiceProvidersRepository,
        service_accounts_repository: ServiceAccountsRepository,
        users_repository: UsersRepository,
    ):
        # Authorization check moved to service layer
        self._validate_admin_permissions(admin_email)
        self.admin_email = admin_email

        # Inject regular repositories
        self.audit_logs_repo = audit_logs_repository
        self.groups_repo = groups_repository
        self.service_providers_repo = service_providers_repository
        self.service_accounts_repo = service_accounts_repository
        self.users_repo = users_repository

    def _validate_admin_permissions(self, admin_email: EmailStr) -> None:
        """Validate that the user has admin permissions."""
        if not admin_email or admin_email not in settings.SUPER_ADMIN_EMAILS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not authorized to perform admin operations.",
            )

    async def get_logs(
        self,
        group_id: int | None = None,
        user_id: int | None = None,
        service_provider_id: int | None = None,
    ):
        """Get audit logs with JSON parsing."""
        log_records = await self.audit_logs_repo.get_logs(
            group_id, user_id, service_provider_id
        )

        logs = [dict(log) for log in log_records]
        for log in logs:
            if log["new_values"]:
                try:
                    log["parsed_values"] = json.loads(log["new_values"])
                except (json.JSONDecodeError, TypeError):
                    log["parsed_values"] = {"error": "Invalid JSON"}
            else:
                log["parsed_values"] = None

        return logs

    async def get_groups(self):
        """Get all groups for admin view."""
        return await self.groups_repo.get_all_groups()

    async def get_group_details(self, group_id: int):
        """Get detailed group information for admin view."""
        # Get group info, users, and scopes in parallel
        group_info = await self.groups_repo.get_all_groups([group_id])
        if not group_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {group_id} not found",
            )

        group_users = await self.groups_repo.get_group_users(group_id)
        group_scopes = await self.groups_repo.get_group_scopes(group_id)

        return {
            "group": group_info[0],
            "users": group_users,
            "scopes": group_scopes,
        }

    async def get_service_providers(self):
        """Get all service providers for admin view."""
        return await self.service_providers_repo.get_all()

    async def get_service_accounts(self, service_provider_id: int):
        """Get service accounts for a service provider."""
        return await self.service_accounts_repo.get_by_service_provider(
            service_provider_id
        )

    async def get_users(self):
        """Get all users for admin view."""
        return await self.users_repo.get_all_users()

    async def get_user_details(self, user_id: int):
        """Get detailed user information for admin view."""
        user_groups = await self.users_repo.get_user_groups(user_id)
        return {"groups": user_groups}
