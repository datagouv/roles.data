# ------- SERVICE FILE -------
from fastapi import HTTPException, status
from pydantic import UUID4

from src.model import UserCreate, UserResponse, UserWithRoleResponse
from src.repositories.users import UsersRepository


class UsersService:
    def __init__(self, user_repository: UsersRepository):
        self.user_repository = user_repository

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        """
        Retrieve user by ID
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )

        return user

    async def get_user_by_sub(self, user_sub: UUID4) -> UserResponse:
        """
        Retrieve user by it's ProConnect sub
        """
        user = await self.user_repository.get_by_sub(user_sub)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found, either it does not exist or it is not verified",
            )
        return user

    async def get_users_by_group_ids(
        self, group_ids: list[int]
    ) -> dict[int, list[UserWithRoleResponse]]:
        """
        Retrieve all users for multiple group IDs in a single query
        Returns a dictionary mapping group_id -> list of users
        """
        return await self.user_repository.get_all_by_group_ids(group_ids)

    async def get_users_by_group_id(self, group_id: int) -> list[UserWithRoleResponse]:
        """
        Retrieve all user for a given group ID
        """
        usersByGroupId = await self.get_users_by_group_ids([group_id])
        if group_id not in usersByGroupId:
            return []
        return usersByGroupId[group_id]

    async def create_user_if_doesnt_exist(self, user_data: UserCreate) -> UserResponse:
        """
        Create/fetch users if they don't exist
        """
        users = await self.create_users_if_dont_exist([user_data])
        return users[0]

    async def create_users_if_dont_exist(
        self, users_data: list[UserCreate]
    ) -> list[UserResponse]:
        """
        Batch create/fetch users if they don't exist
        Returns list of users in the same order as input
        """
        if not users_data:
            return []

        emails = [user.email for user in users_data]
        existing_users = await self.user_repository.get_by_emails(emails)
        existing_emails = {user.email for user in existing_users}

        # Create users that don't exist
        users_to_create = [
            user for user in users_data if user.email not in existing_emails
        ]
        new_users = []
        if users_to_create:
            new_users = await self.user_repository.create_many(users_to_create)

        # Combine existing and new users, maintaining order
        all_users = existing_users + new_users
        email_to_user = {user.email: user for user in all_users}

        return [email_to_user[user.email] for user in users_data]
