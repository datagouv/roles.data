# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends

from ..dependencies import get_users_service
from ..models import UserBase, UserCreate
from ..services.users import UsersService

router = APIRouter(
    prefix="/users",
    tags=["Utilisateurs"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=UserBase)
async def create_user(
    user: UserCreate, users_service: UsersService = Depends(get_users_service)
):
    return await users_service.create_user(user)
