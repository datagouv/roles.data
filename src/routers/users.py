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
async def create(
    user: UserCreate, users_service: UsersService = Depends(get_users_service)
) -> UserResponse:
    """
    Crée l’utilisateur dans la base de données.

    L’utilisateur doit être un utilisateur ProConnect existant.
    """
    return await users_service.create_user(user)


@router.get("/search", response_model=UserResponse)
async def by_email(
    email: EmailStr,
    users_service: UsersService = Depends(get_users_service),
) -> UserResponse:
    """
    Retourne un utilisateur identifié par son adresse e-mail.
    """
    return await users_service.get_user_by_email(email=email)


@router.get("/{user_id}", status_code=200)
async def by_id(
    user_id: int, users_service: UsersService = Depends(get_users_service)
) -> UserResponse:
    """
    Retourne un utilisateur identifié par son ID.
    """
    return await users_service.get_user_by_id(user_id)


@router.patch("/verify", status_code=200)
async def confirm_user(
    user_email: EmailStr,
    user_sub: str,
    users_service: UsersService = Depends(get_users_service),
) -> None:
    """
    Vérifie/confirme un utilisateur et enregistre son sub ProConnect

    Un utilisateur est non vérifié lors de sa création.

    Un utilisateur non vérifié ne peut pas accomplir les actions d’administration d’équipe
    """
    return await users_service.verify_user(user_email, user_sub)
