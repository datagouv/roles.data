# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends, Path, Query
from pydantic import UUID4, EmailStr, HttpUrl

from ..dependencies import get_groups_service
from ..dependencies.auth.o_auth import decode_access_token
from ..model import (
    GroupCreate,
    GroupResponse,
    GroupWithScopesResponse,
    GroupWithUsersAndScopesResponse,
)
from ..services.groups import GroupsService

router = APIRouter(
    prefix="/groups",
    tags=["Gestion des groupes par le fournisseur de service"],
    dependencies=[Depends(decode_access_token)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.get("/all", response_model=list[GroupWithScopesResponse])
async def list_service_provider_groups(
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Liste les groupes disponibles pour votre fournisseur de services.
    """
    return await group_service.list_groups()


@router.get("/{group_id}", response_model=GroupWithUsersAndScopesResponse)
async def by_id(
    group_id: int = Path(..., description="ID du groupe à récupérer"),
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Récupère un groupe par son ID. Inclut les utilisateurs, leurs rôles et les droits du groupes sur le fournisseur de service.
    """
    return await group_service.get_group_with_users_and_scopes(group_id)


# TODO deprecate this route
@router.get("/search", response_model=list[GroupWithUsersAndScopesResponse])
async def search_service_provider_groups_by_user(
    user_email: EmailStr = Query(..., description="Mail de l’utilisateur"),
    user_sub: UUID4 = Query(None, description="Legacy (facultatif)"),
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Recherche les groupes d’un utilisateur, avec son adresse e-mail et son sub ProConnect.
    """
    return await group_service.search_groups(user_email=user_email)


@router.post("/", response_model=GroupResponse, status_code=201)
async def create(
    group: GroupCreate,
    groups_service: GroupsService = Depends(get_groups_service),
) -> GroupResponse:
    """
    Crée un nouveau groupe.

    Si l’organisation n’existe pas encore, elle est créée automatiquement.
    """
    return await groups_service.create_group(group)


@router.patch("/{group_id}/scopes", status_code=200)
async def update_group_scopes(
    group_id: int,
    scopes: str = Query(
        "",
        description="Liste des scopes (facultatif)",
    ),
    contract_description: str = Query(
        None,
        description="Description du contrat (facultatif)",
    ),
    contract_url: HttpUrl = Query(
        None,
        description="Url du contrat (facultatif)",
    ),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Met à jour :
    - les droits ou `scopes` d’un groupe sur votre fournisseur de service
    - le contrat qui lie le groupe à votre fournisseur de service
    """
    return await groups_service.update_or_create_scopes(
        group_id,
        scopes,
        contract_description,
        contract_url,
    )
