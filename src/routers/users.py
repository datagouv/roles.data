# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends
from pydantic import UUID4, EmailStr

from auth.o_auth import decode_access_token

from ..dependencies import get_users_service
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

    Quand l'utilisateur est créé, il est encore non vérifié. Un appel à l'endpoint `/users/verify` permet de le confirmer avec son sub ProConnect.

    Cela permet de créér un utilisateur et de l’ajouter à un groupe sans connaitre son sub.
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
    return await users_service.get_user_by_email(email=email, only_verified_user=False)


@router.get("/{user_id}", status_code=200)
async def by_id(
    user_id: int, users_service: UsersService = Depends(get_users_service)
) -> UserResponse:
    """
    Retourne un utilisateur identifié par son ID.
    """
    return await users_service.get_user_by_id(user_id, only_verified_user=False)


@router.patch("/verify", status_code=200)
async def confirm_user(
    user_email: EmailStr,
    user_sub: UUID4,
    users_service: UsersService = Depends(get_users_service),
) -> UserResponse:
    """
    Enregistre le sub ProConnect d’un utilisateur et permet de "vérifier" l’utilisateur.

    À sa création, seul le mail de l'utilisateur est connu.
    L’utilisateur n’est alors pas vérifié et certaines actions impliquant cet utilisateur sont impossibles.
    """
    return await users_service.verify_user(user_email, user_sub)
