from databases import Database
from fastapi import Depends

from .database import get_db
from .repositories.groups import GroupsRepository
from .repositories.organisations import OrganisationsRepository
from .repositories.users import UsersRepository
from .services.groups import GroupsService
from .services.organisations import OrganisationsService
from .services.users import UsersService


async def get_users_service(db: Database = Depends(get_db)) -> UsersService:
    """
    Dependency function that provides a UsersService instance.

    Args:
        db: Database connection provided by get_db dependency

    Returns:
        An initialized UsersService
    """
    user_repository = UsersRepository(db)
    return UsersService(user_repository)


async def get_groups_service(db: Database = Depends(get_db)) -> GroupsService:
    """
    Dependency function that provides a GroupsService instance.

    Args:
        db: Database connection provided by get_db dependency

    Returns:
        An initialized GroupsService
    """
    groups_repository = GroupsRepository(db)
    return GroupsService(
        groups_repository,
        await get_users_service(db),
        await get_organisations_service(db),
    )


async def get_organisations_service(
    db: Database = Depends(get_db),
) -> OrganisationsService:
    """
    Dependency function that provides a OrganisationsService instance.

    Args:
        db: Database connection provided by get_db dependency

    Returns:
        An initialized OrganisationsService
    """
    organisations_repository = OrganisationsRepository(db)
    return OrganisationsService(organisations_repository)
