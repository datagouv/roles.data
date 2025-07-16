# ------- SERVICE FILE -------
from xmlrpc.client import boolean

from fastapi import HTTPException, status
from pydantic import UUID4

from ..model import UserCreate, UserResponse, UserWithRoleResponse
from ..repositories.users import UsersRepository


class UsersService:
    def __init__(self, user_repository: UsersRepository):
        self.user_repository = user_repository

    async def validate_user_data(self, user_data: UserCreate) -> None:
        if not user_data.email:
            raise ValueError("Email is required.")

    async def verify_user(self, user_email: str, user_sub: UUID4):
        user = await self.get_user_by_email(user_email, only_verified_user=False)
        if user.is_verified:
            verified_user_sub = await self.user_repository.get_user_sub(user_email)
            if str(verified_user_sub["sub_pro_connect"]) != str(user_sub):
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="User is already verified with a different sub.",
                )
        else:
            await self.user_repository.mark_user_as_verified(user_email, user_sub)

    async def get_user_by_email(
        self, email: str, only_verified_user: boolean = True
    ) -> UserResponse:
        """
        Retrieve user by email
        """
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {email} not found",
            )
        if only_verified_user and not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="User is not yet verified.",
            )
        return user

    async def get_user_by_id(
        self, user_id: int, only_verified_user: boolean = True
    ) -> UserResponse:
        """
        Retrieve user by ID
        """
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )
        if only_verified_user and not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="User is not yet verified.",
            )
        return user

    async def get_user_by_sub(self, user_sub: UUID4) -> UserResponse:
        """
        Retrieve user by it's ProConnect sub
        """
        user = await self.user_repository.get_user_by_sub(user_sub)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with sub {user_sub} is not found, either it does not exist or it is not verified",
            )
        return user

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

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        # Business Logic Validation
        await self.validate_user_data(user_data)

        try:
            # this will raise an HTTPException if the user does not exist
            await self.get_user_by_email(user_data.email)

            raise ValueError("User already exists.")
        except HTTPException as e:
            if e.status_code == 404:
                new_user = await self.user_repository.add_user(user_data)
                return new_user
            raise e

    async def create_user_if_doesnt_exist(self, user_data: UserCreate) -> UserResponse:
        try:
            return await self.get_user_by_email(
                user_data.email, only_verified_user=False
            )
        except HTTPException as e:
            if e.status_code == 404:
                return await self.create_user(user_data)
            else:
                raise e
