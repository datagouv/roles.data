# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends
from pydantic import EmailStr

from src.auth import decode_access_token

from ..dependencies import get_users_service
from ..models import UserCreate, UserResponse
from ..services.users import UsersService

router = APIRouter(
    prefix="/users",
    tags=["Utilisateurs"],
    dependencies=[Depends(decode_access_token)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate, users_service: UsersService = Depends(get_users_service)
):
    return await users_service.create_user(user)


@router.get("/search", response_model=UserResponse)
async def get_user_by_email(
    email: EmailStr,
    users_service: UsersService = Depends(get_users_service),
) -> UserResponse:
    """
    Get a specific user by email, including all roles and group memberships.
    """
    return await users_service.get_user_by_email(email=email)


@router.get("/{user_id}", status_code=200)
async def get_user_by_id(
    user_id: int, users_service: UsersService = Depends(get_users_service)
) -> UserResponse:
    """
    Get a user by ID.
    """
    return await users_service.get_user_by_id(user_id)
