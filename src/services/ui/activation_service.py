from fastapi import HTTPException, status
from pydantic import UUID4

from ...model import UserResponse
from ...repositories.users import UsersRepository


class ActivationService:
    def __init__(self, user_repository: UsersRepository):
        self.user_repository = user_repository

    async def activate_user(self, user_email: str, user_sub: UUID4) -> UserResponse:
        users = await self.user_repository.get_by_emails([user_email])

        if len(users) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not validate credentials",
            )

        user = users[0]
        if not user.is_verified:
            return await self.user_repository.activate(
                user_sub=user_sub, user_email=user_email
            )

        return user
