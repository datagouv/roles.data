# ------- SERVICE FILE -------
from uuid import UUID

from fastapi import HTTPException, status

from ..repositories.users_sub import UserSubsRepository


class UserSubsService:
    def __init__(self, user_subs_repository: UserSubsRepository):
        self.user_subs_repository = user_subs_repository

    async def pair(self, user_email: str, user_sub: UUID) -> None:
        """
        If sub is not yet saved, save it in database

        If saved (mail,sub) does not match -> raise an exception

        If user not found raise a 404
        """
        saved_sub = await self.user_subs_repository.get(user_email)

        print(saved_sub, user_sub, user_email)

        if saved_sub == "":
            await self.user_subs_repository.set(user_email, user_sub)

        if not saved_sub:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail=f"User {user_email} not found"
            )

        if saved_sub != user_sub:
            raise HTTPException(
                status.HTTP_423_LOCKED,
                detail=f"User {user_email} already saved with a different sub",
            )
