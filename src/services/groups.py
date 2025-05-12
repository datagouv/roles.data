from fastapi import HTTPException

from src.services.services_provider import ServiceProvidersService

from ..models import (
    GroupCreate,
    GroupResponse,
    GroupWithUsersAndScopesResponse,
    OrganisationCreate,
    UserCreate,
)
from ..repositories import groups
from . import organisations, roles, scopes, users


class GroupsService:
    """
    Service class for managing groups and their users.

    This is the heart of the application

    It uses almost every other services as a group is linked organisation, user, user roles and groups

    It can only be used in the context of a service provider, which is why it takes a service_provider_id as an argument
    in the constructor.
    """

    def __init__(
        self,
        groups_repository: groups.GroupsRepository,
        users_service: users.UsersService,
        roles_service: roles.RolesService,
        organisations_service: organisations.OrganisationsService,
        service_provider_service: ServiceProvidersService,
        scopes_service: scopes.ScopesService,
        service_provider_id: int,
    ):
        self.groups_repository = groups_repository
        self.users_service = users_service
        self.roles_service = roles_service
        self.organisations_service = organisations_service
        self.service_provider_service = service_provider_service
        self.scopes_service = scopes_service
        self.service_provider_id = service_provider_id

    async def validate_group_data(self, group_data: GroupCreate) -> None:
        if not group_data.organisation_siren:
            raise HTTPException(status_code=400, detail="Siren is required.")

    async def get_group_by_id(self, group_id: int) -> GroupResponse:
        group = await self.groups_repository.get_group_by_id(
            group_id, self.service_provider_id
        )
        if not group:
            raise HTTPException(
                status_code=404,
                detail=f"Group with ID {group_id} not found, are you certain it exists and you can use it ?",
            )
        return group

    async def create_group(self, group_data: GroupCreate) -> GroupResponse:
        await self.validate_group_data(group_data)

        orga_id = await self.organisations_service.get_or_create_organisation(
            OrganisationCreate(siren=group_data.organisation_siren)
        )

        try:
            admin_user = await self.users_service.get_user_by_email(
                group_data.admin_email
            )
        except HTTPException as e:
            if e.status_code == 404:
                admin_user = await self.users_service.create_user(
                    UserCreate(email=group_data.admin_email)
                )
            else:
                raise e

        new_group = await self.groups_repository.create_group(
            group_data, orga_id, self.service_provider_id
        )

        await self.add_user_to_group(new_group.id, admin_user.id, role_id=1)

        return new_group

    async def list_groups(self) -> list[GroupResponse]:
        return await self.groups_repository.list_groups(self.service_provider_id)

    async def search_groups(self, email: str) -> list[GroupWithUsersAndScopesResponse]:
        """
        Search for groups by user email.

        This method will return all groups that the user is a member of, regardless of their role.
        """
        user = await self.users_service.get_user_by_email(email)
        groups = await self.groups_repository.search_groups_by_user(
            user.id, self.service_provider_id
        )

        groupsWithUsers = []
        for g in groups:
            # Python's dict() function does not include dynamically added attributes
            # so we have to manually create a dict then a new object
            g_dict = dict(g)
            g_dict["users"] = await self.users_service.get_users_by_group_id(g.id)
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

        scopes = await self.scopes_service.get_scopes(
            self.service_provider_id, group_id
        )

        group_dict["scopes"] = scopes

        return GroupWithUsersAndScopesResponse(**group_dict)

    async def update_group(self, group_id: int, group_name: str) -> GroupResponse:
        group = await self.get_group_by_id(group_id)
        return await self.groups_repository.update_group(group.id, group_name)

    # user management
    async def add_user_to_group(self, group_id: int, user_id: int, role_id: int):
        role = await self.roles_service.get_roles_by_id(role_id)
        user = await self.users_service.get_user_by_id(user_id)
        group = await self.get_group_by_id(group_id)
        return await self.groups_repository.add_user_to_group(
            group.id, user.id, role.id
        )

    async def remove_user_from_group(self, group_id: int, user_id: int):
        user = await self.users_service.get_user_by_id(user_id)
        group = await self.get_group_by_id(group_id)

        return await self.groups_repository.remove_user_from_group(group.id, user.id)

    async def update_user_in_group(self, group_id: int, user_id: int, role_id: int):
        # check if the user, is in the group
        role = await self.roles_service.get_roles_by_id(role_id)
        group = await self.get_group_with_users_and_scopes(group_id)

        if user_id not in [u.id for u in group.users]:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found in group {group_id}",
            )
        return await self.groups_repository.update_user_role_in_group(
            group.id, user_id, role.id
        )

    async def add_scopes(self, group_id: int, scopes: str):
        group = await self.get_group_by_id(group_id)
        service_provider = (
            await self.service_provider_service.get_service_provider_by_id(
                self.service_provider_id
            )
        )

        return await self.scopes_service.grant(service_provider.id, group.id, scopes)

    async def update_scopes(self, group_id: int, scopes: str):
        group = await self.get_group_by_id(group_id)
        service_provider = (
            await self.service_provider_service.get_service_provider_by_id(
                self.service_provider_id
            )
        )

        # verify if the group is already linked to the service provider
        await self.scopes_service.get_scopes(service_provider.id, group.id)
        # check if the group is linked to the service provider
        return await self.scopes_service.update(service_provider.id, group.id, scopes)
