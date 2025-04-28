from fastapi import HTTPException

from ..models import (
    GroupCreate,
    GroupResponse,
    GroupWithUsersResponse,
    OrganisationCreate,
    Siren,
    UserCreate,
)
from ..repositories import groups
from . import organisations, roles, users


class GroupsService:
    def __init__(
        self,
        groups_repository: groups.GroupsRepository,
        users_service: users.UsersService,
        roles_service: roles.RolesService,
        organisations_service: organisations.OrganisationsService,
    ):
        self.groups_repository = groups_repository
        self.users_service = users_service
        self.roles_service = roles_service
        self.organisations_service = organisations_service

    async def validate_group_data(self, group_data: GroupCreate) -> None:
        if not group_data.organisation_siren:
            raise HTTPException(status_code=400, detail="Siren is required.")

    async def create_group(self, group_data: GroupCreate) -> GroupResponse:
        await self.validate_group_data(group_data)

        orga_id = await self.organisations_service.get_or_create_organisation(
            OrganisationCreate(siren=group_data.organisation_siren)
        )
        admin_user = await self.users_service.create_user(
            UserCreate(email=group_data.admin_email), fail_if_already_exist=False
        )
        new_group = await self.groups_repository.create_group(group_data, orga_id)

        await self.add_user_to_group(new_group.id, admin_user.id, role_id=1)

        return new_group

    async def list_groups(self, organisation_siren: Siren) -> list[GroupResponse]:
        return await self.groups_repository.list_groups(organisation_siren)

    async def get_group_with_users(self, group_id: int) -> GroupWithUsersResponse:
        group = await self.groups_repository.get_group_by_id(group_id)

        if not group:
            raise HTTPException(
                status_code=404, detail=f"Group with ID {group_id} not found"
            )

        group.users = await self.users_service.get_users_by_group_id(group_id)
        return group

    async def update_group(self, group_id: int, group_name: str) -> GroupResponse:
        group = await self.groups_repository.get_group_by_id(group_id)
        if not group:
            raise HTTPException(
                status_code=404, detail=f"Group with ID {group_id} not found"
            )

        return await self.groups_repository.update_group(group_id, group_name)

    async def delete_group(self, group_id: int):
        return await self.groups_repository.delete_group(group_id)

    # user management
    async def add_user_to_group(self, group_id: int, user_id: int, role_id: int):
        role = await self.roles_service.get_roles_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=404, detail=f"Role with ID {role_id} not found"
            )

        user = await self.users_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User with ID {user_id} not found"
            )

        group = await self.groups_repository.get_group_by_id(group_id)
        if not group:
            raise HTTPException(
                status_code=404, detail=f"Group with ID {group_id} not found"
            )

        return await self.groups_repository.add_user_to_group(
            group_id, user_id, role_id
        )

    async def remove_user_from_group(self, group_id: int, user_id: int):
        user = await self.users_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User with ID {user_id} not found"
            )

        group = await self.groups_repository.get_group_by_id(group_id)
        if not group:
            raise HTTPException(
                status_code=404, detail=f"Group with ID {group_id} not found"
            )

        return await self.groups_repository.remove_user_from_group(group_id, user_id)

    async def update_user_in_group(self, group_id: int, user_id: int, role_id: bool):
        role = await self.roles_service.get_roles_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=404, detail=f"Role with ID {role_id} not found"
            )

        user = await self.users_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User with ID {user_id} not found"
            )

        group = await self.groups_repository.get_group_by_id(group_id)
        if not group:
            raise HTTPException(
                status_code=404, detail=f"Group with ID {group_id} not found"
            )

        return await self.groups_repository.update_user_role_in_group(
            group_id, user_id, role_id
        )
