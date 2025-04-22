from databases import Database
from fastapi import Depends

from .database import get_db
from .repositories.organisations import OrganisationsRepository
from .repositories.teams import TeamsRepository
from .repositories.users import UsersRepository
from .services.organisations import OrganisationsService
from .services.teams import TeamsService
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


async def get_teams_service(db: Database = Depends(get_db)) -> TeamsService:
    """
    Dependency function that provides a TeamsService instance.

    Args:
        db: Database connection provided by get_db dependency

    Returns:
        An initialized TeamsService
    """
    teams_repository = TeamsRepository(db)
    return TeamsService(
        teams_repository,
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
