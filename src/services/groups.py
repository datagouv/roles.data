from uuid import UUID

from fastapi import HTTPException, status
from pydantic import UUID4, EmailStr, HttpUrl

from src.constants import DEFAULT_PAGE_SIZE, MAX_LISTED_ADMINS
from src.model import (
    GroupCreate,
    GroupResponse,
    GroupWithAdminsAndScopesResponse,
    GroupWithScopesResponse,
    GroupWithUsersAndRoleResponse,
    GroupWithUsersAndScopesResponse,
    OrganisationCreate,
    OrganisationGroupResponse,
    RoleResponse,
    Siret,
    UserCreate,
    UserInGroupCreate,
    UserInGroupResponse,
    build_pagination,
)
from src.repositories import groups, users_in_group
from src.services import organisations, roles, scopes, users
from src.services.email.main import EmailService
from src.services.service_providers import ServiceProvidersService


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
        db_session,
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
        self.db_session = db_session
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

        role = await self.users_service.get_role_in_group(acting_user.id, group_id)

        if not role or not role.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not admin of the group.",
            )

    async def is_member(self, acting_user_sub: UUID4, group_id: int) -> RoleResponse:
        """
        Verify if the user belongs to the group, whatever their role.

        Returns the role they hold in it, which the caller often needs anyway.
        """
        # verify user exists and group exists
        acting_user = await self.users_service.get_user_by_sub(acting_user_sub)
        await self.get_group_by_id(group_id)

        role = await self.users_service.get_role_in_group(acting_user.id, group_id)

        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not member of the group.",
            )

        return role

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

        # Single transaction so that a failure never leaves a partially created group
        async with self.db_session.transaction():
            orga_id = await self.organisations_service.get_or_create_organisation(
                OrganisationCreate(siret=group_data.organisation_siret)
            )

            admin_user = await self.users_service.create_user_if_doesnt_exist(
                group_data.admin
            )

            new_group = await self.groups_repository.create(
                group_data, orga_id, self.service_provider_id
            )

            await self.add_user_to_group(
                new_group.id, user_id=admin_user.id, role_id=1, send_email=False
            )

            if group_data.members:
                members = await self.users_service.create_users_if_dont_exist(
                    group_data.members
                )
                user_role_pairs = [(user.id, 2) for user in members]
                await self.users_in_group_repository.add_users(
                    new_group.id, user_role_pairs
                )

        # Only notify once the group is committed. The admin is the group's first
        # user, so there is no other admin to mention.
        await self.send_nouveau_groupe_email(
            admin_user.email, new_group.name, group_admin_email=None
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

    async def search_groups_by_organisation_siret(
        self, siret: Siret | None
    ) -> list[OrganisationGroupResponse]:
        if not siret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization SIRET is required",
            )
        """
        Search for groups by organisation siret.
        """
        groups_by_siret = await self.groups_repository.search_by_organisation_siret(
            siret, self.service_provider_id
        )

        return [OrganisationGroupResponse(**dict(group)) for group in groups_by_siret]

    async def search_groups(
        self, user_sub: UUID
    ) -> list[GroupWithAdminsAndScopesResponse]:
        """
        Search for groups by user email.

        This method will return all groups that the user is a member of, regardless of their role.

        Each group carries its first admins and the role the user holds in it,
        rather than its users: a group can hold far more users than a listing
        should ever return. Use get_group_with_users_and_scopes to walk through
        the users of one group.
        """

        user = await self.users_service.get_user_by_sub(user_sub)
        groups = await self.groups_repository.search_by_user(
            user.id, self.service_provider_id
        )

        # Batch fetch the admins of all groups
        admins_by_group = await self.users_service.get_admins_by_group_ids(
            [g.id for g in groups], MAX_LISTED_ADMINS
        )

        groupsWithAdmins = []
        for g in groups:
            # Python's dict() function does not include dynamically added attributes
            # so we have to manually create a dict then a new object
            g_dict = dict(g)
            g_dict["admins"] = admins_by_group.get(g.id, [])
            g_dict["current_user_role"] = RoleResponse(
                id=g_dict.pop("current_user_role_id"),
                role_name=g_dict.pop("current_user_role_name"),
                is_admin=g_dict.pop("current_user_is_admin"),
            )
            groupsWithAdmins.append(GroupWithAdminsAndScopesResponse(**g_dict))
        return groupsWithAdmins

    async def get_group_with_users_and_scopes(
        self,
        group_id: int,
        users_page: int = 1,
        users_size: int = DEFAULT_PAGE_SIZE,
    ) -> GroupWithUsersAndScopesResponse:
        """
        Fetch a group with one page of its users.
        """
        group = await self.get_group_by_id(group_id)
        users, total = await self.users_service.get_users_page_by_group_id(
            group_id, users_page, users_size
        )

        # Python's dict() function does not include dynamically added attributes
        # so we have to manually create a dict then a new object
        group_dict = dict(group)
        group_dict["users"] = users
        group_dict["users_pagination"] = build_pagination(users_page, users_size, total)

        scopes_and_contract = await self.scopes_service.get_scopes_and_contract(
            self.service_provider_id, group.id
        )

        group_dict["scopes"] = scopes_and_contract.scopes
        group_dict["contract_description"] = scopes_and_contract.contract_description
        group_dict["contract_url"] = scopes_and_contract.contract_url

        return GroupWithUsersAndScopesResponse(**group_dict)

    async def get_group_with_users_and_role(
        self,
        group_id: int,
        current_user_role: RoleResponse,
        users_page: int = 1,
        users_size: int = DEFAULT_PAGE_SIZE,
    ) -> GroupWithUsersAndRoleResponse:
        """
        Fetch a group with one page of its users and the role of the user asking.
        """
        group = await self.get_group_with_users_and_scopes(
            group_id, users_page, users_size
        )
        return GroupWithUsersAndRoleResponse(
            **dict(group), current_user_role=current_user_role
        )

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
        send_email: bool = True,
    ):
        """
        send_email=False lets a caller wrapping this in its own transaction
        send the email once that transaction is committed.
        """
        if user_email is None and user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must provide either user_email or user_id.",
            )

        # Validate role and group before creating anything
        role = await self.roles_service.get_roles_by_id(role_id)
        group = await self.get_group_by_id(group_id)

        # Single transaction so that a user is never created without being added to the group
        async with self.db_session.transaction():
            if user_email is not None:
                user = await self.users_service.create_user_if_doesnt_exist(
                    UserCreate(email=user_email.lower())
                )
            else:
                user = await self.users_service.get_user_by_id(user_id)

            if await self.users_service.get_role_in_group(user.id, group.id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User with ID {user.id} is already in group {group_id}",
                )

            await self.users_in_group_repository.add_users(
                group.id, [(user.id, role.id)]
            )

        if send_email:
            # The user just added may be an admin themselves, and should not be
            # named as the one to turn to in their own email
            await self.send_nouveau_groupe_email(
                user.email,
                group.name,
                await self.get_first_admin_email(group.id, excluded_user_id=user.id),
            )

        role = await self.roles_service.get_roles_by_id(role.id)
        return UserInGroupResponse(
            **dict(user),
            role_id=role.id,
            role_name=role.role_name,
            is_admin=role.is_admin,
        )

    async def add_users_to_group(
        self, group_id: int, users_in_group: list[UserInGroupCreate]
    ) -> list[UserInGroupResponse]:
        """
        Add several users to a group at once.

        Either every user is added, or none is.
        """
        emails = [user.email.lower() for user in users_in_group]
        duplicated_emails = sorted(
            {email for email in emails if emails.count(email) > 1}
        )
        if duplicated_emails:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Duplicated emails in request: {', '.join(duplicated_emails)}",
            )

        # Validate roles and group before creating anything
        roles_by_id = {}
        for role_id in dict.fromkeys(user.role_id for user in users_in_group):
            roles_by_id[role_id] = await self.roles_service.get_roles_by_id(role_id)
        group = await self.get_group_by_id(group_id)

        # Look the admin up before the new users are added, as some of them may
        # be admins themselves
        group_admin_email = await self.get_first_admin_email(group.id)

        # Single transaction so that a user is never created without being added to the group
        async with self.db_session.transaction():
            users = await self.users_service.create_users_if_dont_exist(
                [UserCreate(email=email) for email in emails]
            )

            user_ids_in_group = await self.users_service.get_user_ids_in_group(
                group.id, [user.id for user in users]
            )
            users_already_in_group = [
                user.id for user in users if user.id in user_ids_in_group
            ]
            if users_already_in_group:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Users with ID {', '.join(str(user_id) for user_id in users_already_in_group)} are already in group {group_id}",
                )

            await self.users_in_group_repository.add_users(
                group.id,
                [
                    (user.id, user_in_group.role_id)
                    for user, user_in_group in zip(users, users_in_group)
                ],
            )

        # One email per user so that members are not disclosed to each other
        for user in users:
            await self.send_nouveau_groupe_email(
                user.email, group.name, group_admin_email
            )

        return [
            UserInGroupResponse(
                **dict(user),
                role_id=roles_by_id[user_in_group.role_id].id,
                role_name=roles_by_id[user_in_group.role_id].role_name,
                is_admin=roles_by_id[user_in_group.role_id].is_admin,
            )
            for user, user_in_group in zip(users, users_in_group)
        ]

    async def send_nouveau_groupe_email(
        self, user_email: str, group_name: str, group_admin_email: str | None
    ):
        if not self.should_send_emails:
            return

        service_provider = (
            await self.service_provider_service.get_service_provider_by_id(
                self.service_provider_id
            )
        )
        self.email_service.nouveau_groupe_email(
            recipients=[user_email],
            group_name=group_name,
            service_provider_name=service_provider.name,
            service_provider_url=service_provider.url,
            group_admin_email=group_admin_email,
        )

    async def remove_user_from_group(self, group_id: int, user_id: int):
        user = await self.users_service.get_user_by_id(user_id)
        group = await self.get_group_by_id(group_id)

        role_in_group = await self.users_service.get_role_in_group(user_id, group_id)
        if role_in_group and role_in_group.is_admin:
            if await self.has_only_one_admin(group_id):
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
            group_admin_email=await self.get_first_admin_email(
                group.id, excluded_user_id=user.id
            ),
        )

        return await self.users_in_group_repository.remove_user(group.id, user.id)

    async def update_user_in_group(self, group_id: int, user_id: int, role_id: int):
        # check if the user, is in the group
        role = await self.roles_service.get_roles_by_id(role_id)
        user = await self.users_service.get_user_by_id(user_id)
        group = await self.get_group_by_id(group_id)

        role_in_group = await self.users_service.get_role_in_group(user_id, group_id)
        if not role_in_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found in group {group_id}",
            )

        if not role.is_admin and role_in_group.is_admin:
            if await self.has_only_one_admin(group_id):
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

    async def has_only_one_admin(self, group_id: int) -> bool:
        """
        Check if a group has only one admin.
        """
        return await self.users_service.count_admins_by_group_id(group_id) == 1

    async def get_first_admin_email(
        self, group_id: int, excluded_user_id: int | None = None
    ) -> str | None:
        """
        Return the first admin email found for a group.

        excluded_user_id leaves one user out, to name an admin other than them.
        """
        admin = await self.users_service.get_first_admin_by_group_id(
            group_id, excluded_user_id
        )
        return str(admin.email) if admin else None
