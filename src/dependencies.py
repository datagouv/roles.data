from databases import Database
from fastapi import Depends

from src.auth import extract_authorized_service_providers_from_token
from src.repositories.auth import AuthRepository
from src.services.auth import AuthService

from .database import get_db
from .repositories.groups import GroupsRepository
from .repositories.organisations import OrganisationsRepository
from .repositories.roles import RolesRepository
from .repositories.users import UsersRepository
from .services.groups import GroupsService
from .services.organisations import OrganisationsService
from .services.roles import RolesService
from .services.users import UsersService


async def get_auth_service(
    db: Database = Depends(get_db),
) -> AuthService:
    """
    Dependency function that provides an AuthService instance.
    """
    auth_repository = AuthRepository(db)
    return AuthService(auth_repository)


async def get_users_service(db: Database = Depends(get_db)) -> UsersService:
    """
    Dependency function that provides a UsersService instance.
    """
    users_repository = UsersRepository(db)
    return UsersService(users_repository)


async def get_organisations_service(
    db: Database = Depends(get_db),
) -> OrganisationsService:
    """
    Dependency function that provides a OrganisationsService instance.
    """
    organisations_repository = OrganisationsRepository(db)
    return OrganisationsService(organisations_repository)


async def get_roles_service(db: Database = Depends(get_db)) -> RolesService:
    """
    Dependency function that provides a RolesService instance.
    """
    roles_repository = RolesRepository(db)
    return RolesService(roles_repository)


async def get_groups_service(
    db: Database = Depends(get_db),
    users_service: UsersService = Depends(get_users_service),
    roles_service: RolesService = Depends(get_roles_service),
    organisations_service: OrganisationsService = Depends(get_organisations_service),
    authorized_service_providers: list[int] = Depends(
        extract_authorized_service_providers_from_token
    ),
) -> GroupsService:
    """
    Dependency function that provides a GroupsService instance.
    """
    groups_repository = GroupsRepository(db, authorized_service_providers)
    return GroupsService(
        groups_repository, users_service, roles_service, organisations_service
    )
