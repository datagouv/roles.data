# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import UUID4, EmailStr

from src.auth.o_auth import decode_access_token
from src.dependencies import get_groups_service

from ..model import (
    GroupCreate,
    GroupResponse,
    GroupWithScopesResponse,
    GroupWithUsersAndScopesResponse,
)
from ..services.groups import GroupsService

router = APIRouter(
    prefix="/groups",
    tags=["Groupes"],
    dependencies=[Depends(decode_access_token)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.get("/", response_model=list[GroupWithScopesResponse])
async def list_groups(
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Liste les groupes disponibles pour votre fournisseur de services.
    """
    return await group_service.list_groups()


@router.get("/search", response_model=list[GroupWithUsersAndScopesResponse])
async def search(
    user_email: EmailStr = Query(..., description="Mail de l’utilisateur"),
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Recherche les groupes d’un utilisateur, avec son adresse e-mail et son sub ProConnect.
    """
    return await group_service.search_groups(user_email=user_email)


@router.get("/{group_id}", response_model=GroupWithUsersAndScopesResponse)
async def by_id(
    group_id: int = Path(..., description="ID du groupe à récupérer"),
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Récupère un groupe par son ID. Inclut les utilisateurs, leurs rôles et les droits du groupes sur le fournisseur de service.
    """
    return await group_service.get_group_with_users_and_scopes(group_id)


@router.post("/", response_model=GroupResponse, status_code=201)
async def create(
    group: GroupCreate,
    # sub de l'utilisateur, utilisé par les dépendances
    acting_user_sub: UUID4 = Query(
        None,
        description="Sub ProConnect de l’utilisateur effectuant la demande de création de groupe. Si l’appel est executé côté serveur, signalez-le avec le paramètre `no_acting_user`",
    ),
    no_acting_user: bool = Query(
        False,
        description="Indique si l'appel est effectué côté serveur. Permet de créer un groupe sans l'intervention d’un utilisateur ProConnecté. Si mis à `True`, `acting_user_sub` n'est pas requis.",
    ),
    groups_service: GroupsService = Depends(get_groups_service),
) -> GroupResponse:
    """
    Crée un nouveau groupe.

    Si l’organisation n’existe pas encore, elle est créée automatiquement.
    """

    if not no_acting_user and not acting_user_sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either provide an acting_user_sub or make the call from the server side",
        )

    return await groups_service.create_group(group)
