from fastapi import HTTPException, status
from pydantic import UUID4

from ...model import UserResponse
from ...repositories.service_providers import ServiceProvidersRepository
from ...repositories.users import UsersRepository


class ActivationService:
    def __init__(
        self,
        users_repository: UsersRepository,
        service_providers_repository: ServiceProvidersRepository,
    ):
        self.users_repository = users_repository
        self.service_providers_repository = service_providers_repository

    async def activate_user(self, user_email: str, user_sub: UUID4) -> UserResponse:
        users = await self.users_repository.get_by_emails([user_email])

        if len(users) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not validate credentials",
            )

        user = users[0]
        if not user.is_verified:
            return await self.users_repository.activate(
                user_sub=user_sub, user_email=user_email
            )

        return user

    async def get_user_providers(self, user_email: str):
        return await self.service_providers_repository.find_by_user(user_email)
