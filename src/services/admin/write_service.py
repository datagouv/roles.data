from fastapi import HTTPException, status

from src.model import GroupResponse, ServiceProviderResponse, UserCreate
from src.repositories.admin.admin_read_repository import AdminReadRepository
from src.repositories.groups import GroupsRepository
from src.repositories.admin.admin_write_repository import AdminWriteRepository
from src.repositories.users_in_group import UsersInGroupRepository
from src.services.roles import RolesService
from src.services.users import UsersService
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

    def __init__(
        self,
        admin_read_repository: AdminReadRepository,
        admin_write_repository: AdminWriteRepository,
        groups_repository: GroupsRepository,
        users_in_group_repository: UsersInGroupRepository,
        users_service: UsersService,
        roles_service: RolesService,
    ):
        self.admin_read_repository = admin_read_repository
        self.admin_write_repository = admin_write_repository
        self.groups_repository = groups_repository
        self.users_in_group_repository = users_in_group_repository
        self.users_service = users_service
        self.roles_service = roles_service

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

    async def add_user_to_group(
        self,
        group_id: int,
        user_email: str,
        role_id: int,
    ) -> None:
        """
        Add a user to a group from the admin interface.
        """
        normalized_email = user_email.strip()
        if not normalized_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email cannot be empty.",
            )

        await self._get_group(group_id)
        group_users = await self.admin_read_repository.read_group_users(group_id)
        if any(str(user["email"]).lower() == normalized_email.lower() for user in group_users):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User {normalized_email} is already in group {group_id}.",
            )

        role = await self.roles_service.get_roles_by_id(role_id)
        user = await self.users_service.create_user_if_doesnt_exist(
            UserCreate(email=normalized_email)
        )
        await self.users_in_group_repository.add_users(group_id, [(user.id, role.id)])

    async def update_group_user_role(
        self,
        group_id: int,
        user_id: int,
        role_id: int,
    ) -> None:
        """
        Update a user's role in a group from the admin interface.
        """
        role = await self.roles_service.get_roles_by_id(role_id)
        group_users = await self.admin_read_repository.read_group_users(group_id)
        group_user = next((user for user in group_users if user["id"] == user_id), None)

        if not group_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found in group {group_id}.",
            )

        if not role.is_admin and self._is_only_admin(group_users, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Impossible to update user {user_id} role in group {group_id} "
                    "as it is the only admin of the group."
                ),
            )

        await self.users_in_group_repository.update_user_role(group_id, user_id, role.id)

    async def remove_user_from_group(self, group_id: int, user_id: int) -> None:
        """
        Remove a user from a group from the admin interface.
        """
        group_users = await self.admin_read_repository.read_group_users(group_id)
        group_user = next((user for user in group_users if user["id"] == user_id), None)

        if not group_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found in group {group_id}.",
            )

        if self._is_only_admin(group_users, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Impossible to remove user {user_id} from group {group_id} "
                    "as it is the only admin of the group."
                ),
            )

        await self.users_in_group_repository.remove_user(group_id, user_id)

    async def update_group_name(
        self,
        group_id: int,
        group_name: str,
    ) -> GroupResponse:
        """
        Update a group's name from the admin interface.
        """
        normalized_name = group_name.strip()
        if not normalized_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group name cannot be empty.",
            )

        updated_group = await self.groups_repository.update(group_id, normalized_name)
        if not updated_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {group_id} not found",
            )

        return updated_group

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

    async def delete_user(self, user_id: int) -> None:
        """
        Delete a user and all their relationships.
        Only super admin can delete users.
        """
        return await self.admin_write_repository.delete_user(user_id)

    async def _get_group(self, group_id: int) -> dict:
        groups = await self.admin_read_repository.read_groups([group_id])
        if not groups:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {group_id} not found",
            )
        return dict(groups[0])

    def _is_only_admin(self, group_users: list[dict], user_id: int) -> bool:
        admin_users = [user for user in group_users if user["role"] == "administrateur"]
        return len(admin_users) == 1 and any(user["id"] == user_id for user in admin_users)
