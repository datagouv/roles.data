from databases import Database
from fastapi import Depends

from .database import get_db
from .repositories.users import UsersRepository
from .services.users import UsersService


async def get_user_service(db: Database = Depends(get_db)) -> UsersService:
    """
    Dependency function that provides a UsersService instance.

    Args:
        db: Database connection provided by get_db dependency

    Returns:
        An initialized UserService
    """
    user_repository = UsersRepository(db)
    return UsersService(user_repository)
