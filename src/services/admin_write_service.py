from fastapi import HTTPException, status
from pydantic import EmailStr

from src.config import settings
from src.repositories.groups import GroupsRepository
from src.repositories.service_accounts import ServiceAccountsRepository
from src.repositories.service_providers import ServiceProvidersRepository
from src.utils.security import generate_random_password, hash_password


class AdminWriteService:
    """
    Service class for admin write operations with proper authorization.

    Handles business logic and security for admin operations, reusing existing repositories.
    Should only be called from the web interface!
    """

    def __init__(
        self,
        admin_email: EmailStr,
        groups_repository: GroupsRepository,
        service_providers_repository: ServiceProvidersRepository,
        service_accounts_repository: ServiceAccountsRepository,
    ):
        # Authorization check moved to service layer
        self._validate_admin_permissions(admin_email)
        self.admin_email = admin_email

        # Inject regular repositories
        self.groups_repo = groups_repository
        self.service_providers_repo = service_providers_repository
        self.service_accounts_repo = service_accounts_repository

    def _validate_admin_permissions(self, admin_email: EmailStr) -> None:
        """Validate that the user has admin permissions."""
        if not admin_email or admin_email not in settings.SUPER_ADMIN_EMAILS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not authorized to perform admin operations.",
            )

    async def update_service_account(
        self,
        service_provider_id: int,
        service_account_id: int,
        action: str,
    ) -> str | None:
        """Update a service account with admin actions."""
        if action == "activate":
            await self.service_accounts_repo.update(
                service_provider_id, service_account_id, is_active=True
            )
        elif action == "deactivate":
            await self.service_accounts_repo.update(
                service_provider_id, service_account_id, is_active=False
            )
        elif action == "reset_secret":
            new_password = generate_random_password()
            new_hashed_password = hash_password(new_password)
            await self.service_accounts_repo.update(
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

    async def create_service_account(
        self, service_provider_id: int, client_id: str
    ) -> str:
        """Create a new service account."""
        new_password = generate_random_password()
        new_hashed_password = hash_password(new_password)

        await self.service_accounts_repo.create(
            client_id, service_provider_id, new_hashed_password
        )

        return new_password

    async def create_service_provider(self, name: str, url: str):
        """Create a new service provider."""
        return await self.service_providers_repo.create(name, url)

    async def set_admin(self, group_id: int, user_id: int) -> None:
        """Set a user as admin in a group."""
        await self.groups_repo.set_user_admin(group_id, user_id)
