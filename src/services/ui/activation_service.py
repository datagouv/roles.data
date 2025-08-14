from pydantic import UUID4

from ...model import UserResponse
from ...repositories.users import UsersRepository


class ActivationService:
    def __init__(self, user_repository: UsersRepository):
        self.user_repository = user_repository

    async def activate_user(self, user_email: str, user_sub: UUID4) -> UserResponse:
        user = await self.user_repository.get_by_email(email=user_email)

        if not user.is_verified:
            return await self.user_repository.activate(
                user_sub=user_sub, user_email=user_email
            )

        return user
