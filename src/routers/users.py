# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends
from pydantic import EmailStr

from ..dependencies import get_users_service
from ..dependencies.auth.o_auth import decode_access_token
from ..model import UserCreate, UserResponse
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

    Quand l'utilisateur est créé, il est encore non vérifié. L'utilisateur recevra un email avec un lien de confirmation pour activer son compte.

    Cela permet de créér un utilisateur et de l'ajouter à un groupe sans connaitre son sub.
    """
    return await users_service.create_user_if_doesnt_exist(user)


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
