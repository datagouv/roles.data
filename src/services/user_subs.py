# ------- SERVICE FILE -------
from uuid import UUID

from asyncpg import UniqueViolationError
from fastapi import HTTPException, status

from ..repositories.users_sub import UserSubsRepository


class UserSubsService:
    def __init__(self, user_subs_repository: UserSubsRepository):
        self.user_subs_repository = user_subs_repository

    async def pair(self, user_email: str, user_sub: UUID) -> None:
        """
        If sub is not yet saved, save it in database

        If saved (mail,sub) does not match or user not found raise a 403
        """
        saved_sub = await self.user_subs_repository.get(user_email)

        if saved_sub == "":
            try:
                await self.user_subs_repository.set(user_email, user_sub)
                return
            except UniqueViolationError:
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN,
                    detail="Sub already paired to a different email",
                )

        if not saved_sub:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, detail=f"User {user_email} not found"
            )

        if str(saved_sub) != str(user_sub):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail=f"User {user_email} already saved with a different sub",
            )
