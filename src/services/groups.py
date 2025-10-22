from uuid import UUID

from fastapi import HTTPException, status
from pydantic import UUID4, EmailStr, HttpUrl

from ..model import (
    GroupCreate,
    GroupResponse,
    GroupWithScopesResponse,
    GroupWithUsersAndScopesResponse,
    OrganisationCreate,
    UserCreate,
    UserInGroupResponse,
)
from ..repositories import groups, users_in_group
from . import organisations, roles, scopes, users
from .email.main import EmailService
from .service_providers import ServiceProvidersService


class GroupsService:
    """
    Service class for managing groups and their users.

    This is the heart of the application

    It uses almost every other services as a group is linked organisation, user, user roles and groups

    It can only be used in the context of a service provider, which is why it takes a service_provider_id as an argument
    in the constructor. Note: service_provider_id refers to the business entity ID, not the OAuth2 client credentials.
    """

    def __init__(
        self,
        groups_repository: groups.GroupsRepository,
        users_in_group_repository: users_in_group.UsersInGroupRepository,
        users_service: users.UsersService,
        roles_service: roles.RolesService,
        organisations_service: organisations.OrganisationsService,
        service_provider_service: ServiceProvidersService,
        scopes_service: scopes.ScopesService,
        service_provider_id: int,
        email_service: EmailService,
        should_send_emails: bool,
    ):
        self.groups_repository = groups_repository
        self.users_in_group_repository = users_in_group_repository
        self.users_service = users_service
        self.roles_service = roles_service
        self.organisations_service = organisations_service
        self.service_provider_service = service_provider_service
        self.scopes_service = scopes_service
        self.email_service = email_service
        self.service_provider_id = service_provider_id
        self.should_send_emails = should_send_emails

    async def validate_group_data(self, group_data: GroupCreate) -> None:
        if not group_data.organisation_siret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Siret is required."
            )

    async def is_admin(self, acting_user_sub: UUID4, group_id: int) -> None:
        """
        Verify if the user is an admin of the group.
        """
        # verify user exists and group exists
        acting_user = await self.users_service.get_user_by_sub(acting_user_sub)
        await self.get_group_by_id(group_id)

        group_users = await self.users_service.get_users_by_group_id(group_id)

        if acting_user.id not in [u.id for u in group_users if u.is_admin]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not admin of the group.",
            )

    async def get_group_by_id(self, group_id: int) -> GroupResponse:
        group = await self.groups_repository.get(group_id, self.service_provider_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with ID {group_id} not found, are you certain it exists and you can use it ?",
            )
        return group

    async def create_group(self, group_data: GroupCreate) -> GroupResponse:
        await self.validate_group_data(group_data)

        orga_id = await self.organisations_service.get_or_create_organisation(
            OrganisationCreate(siret=group_data.organisation_siret)
        )

        admin_user = await self.users_service.create_user_if_doesnt_exist(
            group_data.admin
        )

        new_group = await self.groups_repository.create(
            group_data, orga_id, self.service_provider_id
        )

        await self.add_user_to_group(new_group.id, user_id=admin_user.id, role_id=1)

        if group_data.members:
            members = await self.users_service.create_users_if_dont_exist(
                group_data.members
            )
            user_role_pairs = [(user.id, 2) for user in members]
            await self.users_in_group_repository.add_users(
                new_group.id, user_role_pairs
            )

        return new_group

    async def list_groups(self) -> list[GroupWithScopesResponse]:
        return await self.groups_repository.get_all(self.service_provider_id)

    async def search_groups_by_contract(
        self, contract_description: str
    ) -> list[GroupResponse]:
        """
        Search for groups that match a given contract description.
        """

        return await self.groups_repository.search_by_contract(
            contract_description, self.service_provider_id
        )

    async def search_groups(
        self, user_sub: UUID
    ) -> list[GroupWithUsersAndScopesResponse]:
        """
        Search for groups by user email.

        This method will return all groups that the user is a member of, regardless of their role.
        """

        user = await self.users_service.get_user_by_sub(user_sub)
        groups = await self.groups_repository.search_by_user(
            user.id, self.service_provider_id
        )

        # Batch fetch users for all groups
        group_ids = [g.id for g in groups]
        users_by_group = await self.users_service.get_users_by_group_ids(group_ids)

        groupsWithUsers = []
        for g in groups:
            # Python's dict() function does not include dynamically added attributes
            # so we have to manually create a dict then a new object
            g_dict = dict(g)
            g_dict["users"] = users_by_group.get(g.id, [])
            groupsWithUsers.append(GroupWithUsersAndScopesResponse(**g_dict))
        return groupsWithUsers

    async def get_group_with_users_and_scopes(
        self, group_id: int
    ) -> GroupWithUsersAndScopesResponse:
        group: GroupResponse = await self.get_group_by_id(group_id)
        group_dict = dict(group)

        users = await self.users_service.get_users_by_group_id(group_id)

        # Python's dict() function does not include dynamically added attributes
        # so we have to manually create a dict then a new object
        group_dict["users"] = users

        scopes_and_contract = await self.scopes_service.get_scopes_and_contract(
            self.service_provider_id, group_id
        )

        group_dict["scopes"] = scopes_and_contract.scopes
        group_dict["contract_description"] = scopes_and_contract.contract_description
        group_dict["contract_url"] = scopes_and_contract.contract_url

        return GroupWithUsersAndScopesResponse(**group_dict)

    async def update_group(self, group_id: int, group_name: str) -> GroupResponse:
        group = await self.get_group_by_id(group_id)
        return await self.groups_repository.update(group.id, group_name)

    # user management
    async def add_user_to_group(
        self,
        group_id: int,
        role_id: int,
        user_email: EmailStr | None = None,
        user_id: int | None = None,
    ):
        if user_email is not None:
            user = await self.users_service.create_user_if_doesnt_exist(
                UserCreate(email=user_email)
            )
        elif user_id is not None:
            user = await self.users_service.get_user_by_id(user_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must provide either user_email or user_id.",
            )

        role = await self.roles_service.get_roles_by_id(role_id)
        group = await self.get_group_with_users_and_scopes(group_id)

        if self.is_user_in_group(group, user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User with ID {user.id} is already in group {group_id}",
            )

        await self.users_in_group_repository.add_users(group.id, [(user.id, role.id)])

        service_provider = (
            await self.service_provider_service.get_service_provider_by_id(
                self.service_provider_id
            )
        )

        if self.should_send_emails:
            self.email_service.nouveau_groupe_email(
                recipients=[user.email],
                group_name=group.name,
                service_provider_name=service_provider.name,
                service_provider_url=service_provider.url,
            )

        role = await self.roles_service.get_roles_by_id(role.id)
        return UserInGroupResponse(
            **dict(user),
            role_id=role.id,
            role_name=role.role_name,
            is_admin=role.is_admin,
        )

    async def remove_user_from_group(self, group_id: int, user_id: int):
        user = await self.users_service.get_user_by_id(user_id)
        group = await self.get_group_with_users_and_scopes(group_id)

        if self.is_user_admin(group, user_id):
            if self.has_only_one_admin(group):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Impossible to remove user {user_id} from group {group_id} as it is the only admin of the group.",
                )

        service_provider = (
            await self.service_provider_service.get_service_provider_by_id(
                self.service_provider_id
            )
        )

        self.email_service.suppression_email(
            recipients=[user.email],
            group_name=group.name,
            service_provider_name=service_provider.name,
            service_provider_url=service_provider.url,
        )

        return await self.users_in_group_repository.remove_user(group.id, user.id)

    async def update_user_in_group(self, group_id: int, user_id: int, role_id: int):
        # check if the user, is in the group
        role = await self.roles_service.get_roles_by_id(role_id)
        user = await self.users_service.get_user_by_id(user_id)
        group = await self.get_group_with_users_and_scopes(group_id)

        if not self.is_user_in_group(group, user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found in group {group_id}",
            )

        if not role.is_admin:
            if self.has_only_one_admin(group):
                if self.is_user_admin(group, user_id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Impossible to update user {user_id} role in group {group_id} as it is the only admin of the group.",
                    )

        await self.users_in_group_repository.update_user_role(
            group.id, user_id, role.id
        )

        return UserInGroupResponse(
            **dict(user),
            role_id=role.id,
            role_name=role.role_name,
            is_admin=role.is_admin,
        )

    async def update_or_create_scopes(
        self,
        group_id: int,
        scopes: str = "",
        contract_description: str | None = None,
        contract_url: HttpUrl | None = None,
    ):
        """
        Update or establish a relation between a service_provider and a group
        """
        # verify service provider exists
        service_provider = (
            await self.service_provider_service.get_service_provider_by_id(
                self.service_provider_id
            )
        )

        return await self.scopes_service.update_or_create(
            service_provider.id, group_id, scopes, contract_description, contract_url
        )

    def is_user_in_group(
        self, group: GroupWithUsersAndScopesResponse, user_id: int
    ) -> bool:
        """
        Check if a user is in a group.
        """
        return user_id in [u.id for u in group.users]

    def is_user_admin(
        self, group: GroupWithUsersAndScopesResponse, user_id: int
    ) -> bool:
        """
        Check if a user is an admin of a group.
        """
        return next((u.is_admin for u in group.users if u.id == user_id), False)

    def has_only_one_admin(self, group: GroupWithUsersAndScopesResponse) -> bool:
        """
        Check if a group has only one admin.
        """
        return len([u.id for u in group.users if u.is_admin]) == 1
