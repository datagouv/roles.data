from fastapi import HTTPException, status

from src.model import ServiceProviderResponse
from src.repositories.admin.admin_write_repository import AdminWriteRepository
from src.utils.security import generate_random_password, hash_password


class AdminWriteService:
    """
    Service class for admin operations, providing methods to interact with the admin_write_repository.

    Should only be called from the web interface !

    Note on architecture :
    - admin operation are few and very sensitive
    - they should never be exposed to the API
    - thus it is preferrable to centralize them in a single service class rather that DDD driven architecture
    - Security is more important than clean architecture here
    """

    def __init__(self, admin_write_repository: AdminWriteRepository):
        self.admin_write_repository = admin_write_repository

    async def update_service_account(
        self,
        service_provider_id: int,
        service_account_id: int,
        action: str,
    ) -> str | None:
        if action == "activate":
            await self.admin_write_repository.update_service_account(
                service_provider_id, service_account_id, is_active=True
            )
        elif action == "deactivate":
            await self.admin_write_repository.update_service_account(
                service_provider_id, service_account_id, is_active=False
            )
        elif action == "reset_secret":
            new_password = generate_random_password()
            new_hashed_password = hash_password(new_password)
            await self.admin_write_repository.update_service_account(
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
        self,
        service_provider_id: int,
        client_id: str,
    ) -> None:
        """
        Create a new service account.
        """
        new_password = generate_random_password()
        new_hashed_password = hash_password(new_password)
        return await self.admin_write_repository.create_service_account(
            client_id, service_provider_id, new_hashed_password
        )

    async def set_admin(
        self,
        group_id: int,
        user_id: int,
    ):
        """
        Set a user as admin of a specific group.
        """
        return await self.admin_write_repository.set_admin(group_id, user_id)

    async def create_service_provider(
        self, name: str, url: str, proconnect_client_id: str | None = None
    ) -> ServiceProviderResponse:
        """
        Create a new service provider.
        """
        return await self.admin_write_repository.create_service_provider(
            name, url, proconnect_client_id
        )

    async def update_service_provider(
        self,
        service_provider_id: int,
        name: str,
        url: str,
        proconnect_client_id: str | None = None,
    ) -> ServiceProviderResponse:
        """
        Update a service provider name, url, and proconnect_client_id
        """
        return await self.admin_write_repository.update_service_provider(
            service_provider_id, name, url, proconnect_client_id
        )

    async def delete_group(self, group_id: int) -> None:
        """
        Delete a group and all its related data.
        Only super admin can delete groups.
        """
        return await self.admin_write_repository.delete_group(group_id)
