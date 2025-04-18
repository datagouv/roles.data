from databases import Database
from fastapi import Depends

from .database import get_db
from .repositories.users import UserRepository
from .services.user import UserService


async def get_user_service(db: Database = Depends(get_db)) -> UserService:
    """
    Dependency function that provides a UserService instance.

    Args:
        db: Database connection provided by get_db dependency

    Returns:
        An initialized UserService
    """
    user_repository = UserRepository(db)
    return UserService(user_repository)
