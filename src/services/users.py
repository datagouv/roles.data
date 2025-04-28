# ------- SERVICE FILE -------
from ..models import UserCreate, UserResponse, UserWithRoleResponse
from ..repositories.users import UsersRepository


class UsersService:
    def __init__(self, user_repository: UsersRepository):
        self.user_repository = user_repository

    async def validate_user_data(self, user_data: UserCreate) -> None:
        if not user_data.email:
            raise ValueError("Email is required.")

    async def get_user_by_email(self, email: str) -> UserResponse:
        """
        Retrieve user by email
        """
        return await self.user_repository.get_user_by_email(email)

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        """
        Retrieve user by ID
        """
        return await self.user_repository.get_user_by_id(user_id)

    async def get_users_by_group_id(self, group_id: int) -> list[UserWithRoleResponse]:
        """
        Retrieve all user for a given group ID
        """
        return await self.user_repository.get_users_by_group_id(group_id)

    async def check_user_exists(self, email: str) -> bool:
        existing_user = await self.user_repository.get_user_by_email(email)

        if existing_user:
            return True
        return False

    async def create_user(
        self, user_data: UserCreate, fail_if_already_exist=True
    ) -> UserResponse:
        # Business Logic Validation
        await self.validate_user_data(user_data)

        user = await self.get_user_by_email(user_data.email)

        if user:
            if fail_if_already_exist:
                raise ValueError("User already exists.")
            return user
        else:
            return await self.user_repository.add_user(user_data)

    async def delete_user(self, user_id: int) -> None:
        """
        Retrieve user by ID
        """
        return await self.user_repository.delete_user(user_id)
