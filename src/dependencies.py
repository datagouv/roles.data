from databases import Database
from fastapi import Depends

from .database import get_db
from .repositories.members import MemberRepository
from .services.member import MemberService


async def get_member_service(db: Database = Depends(get_db)) -> MemberService:
    """
    Dependency function that provides a MemberService instance.

    Args:
        db: Database connection provided by get_db dependency

    Returns:
        An initialized MemberService
    """
    member_repository = MemberRepository(db)
    return MemberService(member_repository)
