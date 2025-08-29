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
        user = await self.users_repository.get_by_email(email=user_email)

        if not user.is_verified:
            return await self.users_repository.activate(
                user_sub=user_sub, user_email=user_email
            )

        return user

    async def get_user_providers(self, user_email: str):
        return await self.service_providers_repository.find_by_user(user_email)
