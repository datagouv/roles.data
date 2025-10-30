# ------- SERVICE FILE -------
from uuid import UUID

from asyncpg import UniqueViolationError
from fastapi import HTTPException, status
from pydantic import EmailStr

from src.repositories.users_sub import UserSubsRepository


class UserSubsService:
    def __init__(self, user_subs_repository: UserSubsRepository):
        self.user_subs_repository = user_subs_repository

    async def get_email(self, user_sub: UUID) -> EmailStr | None:
        """
        Get email if sub in DB
        """
        return await self.user_subs_repository.get_mail_by_sub(user_sub)

    async def pair(self, user_email: str, user_sub: UUID) -> None:
        """
        If sub is not yet saved, save it in database

        If saved (mail,sub) does not match or user not found raise a 403
        """
        sub = await self.user_subs_repository.get_sub_by_email(user_email)

        if sub is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=f"User {user_email} not found"
            )

        if str(sub) != "":
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail=f"User {user_email} already saved with a different sub",
            )

        try:
            await self.user_subs_repository.set(email=user_email, sub=user_sub)
            return
        except UniqueViolationError:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Sub already paired to a different email",
            )
