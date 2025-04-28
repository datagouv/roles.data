# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends, Query
from pydantic import EmailStr

from ..dependencies import get_users_service
from ..models import UserBase, UserCreate, UserResponse
from ..services.users import UsersService

router = APIRouter(
    prefix="/users",
    tags=["Utilisateurs"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.post("/", response_model=UserBase)
async def create_user(
    user: UserCreate, users_service: UsersService = Depends(get_users_service)
):
    return await users_service.create_user(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int, users_service: UsersService = Depends(get_users_service)
):
    """
    Delete a user by ID.
    """
    await users_service.delete_user(user_id)


@router.get("/{user_id}", status_code=200)
async def get_user_by_id(
    user_id: int, users_service: UsersService = Depends(get_users_service)
):
    """
    Get a user by ID.
    """
    await users_service.get_user_by_id(user_id)


@router.get("/", response_model=UserResponse)
async def get_user_by_email(
    filter: EmailStr = Query(
        ..., description="The email of the user to retrieve or the group ID"
    ),
    users_service: UsersService = Depends(get_users_service),
):
    """
    Get a specific user by email, including all roles and group memberships.
    """

    user = await users_service.get_user_by_email(email=filter)
    return user
