# ------- SERVICE FILE -------
from ..models import UserBase, UserCreate
from ..repositories.users import UsersRepository


class UsersService:
    def __init__(self, user_repository: UsersRepository):
        self.user_repository = user_repository

    async def validate_user_data(self, user_data: UserCreate) -> None:
        if not user_data.email:
            raise ValueError("Email is required.")

    async def check_user_exists(self, email: str) -> None:
        existing_user = await self.user_repository.get_user_by_email(email)
        if existing_user:
            raise ValueError("user already exists.")

    async def create_user(self, user_data: UserCreate) -> UserBase:
        # Business Logic Validation
        await self.validate_user_data(user_data)
        await self.check_user_exists(user_data.email)

        new_user_id = await self.user_repository.add_user(user_data)

        return await self.user_repository.get_user_by_id(new_user_id)
