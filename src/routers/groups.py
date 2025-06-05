# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends, Path, Query
from pydantic import EmailStr

from src.auth import decode_access_token
from src.dependencies import get_groups_service, get_users_service
from src.services.users import UsersService

from ..models import GroupCreate, GroupResponse, GroupWithUsersAndScopesResponse
from ..services.groups import GroupsService

router = APIRouter(
    prefix="/groups",
    tags=["Équipes"],
    dependencies=[Depends(decode_access_token)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.get("/", response_model=list[GroupResponse])
async def list_groups(
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Liste les équipes disponibles pour votre fournisseur de services.
    """
    return await group_service.list_groups()


@router.get("/search", response_model=list[GroupWithUsersAndScopesResponse])
async def search(
    email: EmailStr = Query(..., description="Mail de l’utilisateur"),
    acting_user_sub: str | None = Query(
        None, description="Sub de l’utilisateur (facultatif)"
    ),
    users_service: UsersService = Depends(get_users_service),
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Recherche les équipes d’un utilisateur vérifié, avec son adresse e-mail.

    Si l'utilisateur n'est pas encore vérifié, l’appel échouera et vous devrez vérifier l'utilisateur (cf. `/users/verify`).

    Il est possible de passer en argument `acting_user_sub` qui permet de se passer d’un appel à `/user/verify`
    """

    if acting_user_sub:
        await users_service.verify_user(user_sub=acting_user_sub, user_email=email)

    return await group_service.search_groups(email=email)


@router.get("/{group_id}", response_model=GroupWithUsersAndScopesResponse)
async def by_id(
    group_id: int = Path(..., description="ID du groupe à récupérer"),
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Récupère une équipe par son ID. Inclut les utilisateurs, leurs rôles et les droits du groupes sur le fournisseur de service.
    """
    return await group_service.get_group_with_users_and_scopes(group_id)


@router.post("/", response_model=GroupResponse, status_code=201)
async def create(
    group: GroupCreate,
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Crée une nouvelle équipe.

    Si l’organisation n’existe pas encore, elle est créée automatiquement.
    """
    return await groups_service.create_group(group)
