# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends, Path, Query
from pydantic import HttpUrl

from src.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from src.dependencies import get_groups_service
from src.dependencies.auth.o_auth import decode_access_token
from src.model import (
    GroupCreate,
    GroupResponse,
    GroupWithScopesResponse,
    GroupWithUsersAndScopesResponse,
)
from src.services.groups import GroupsService

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
    users_page: int = Query(
        1, ge=1, alias="usersPage", description="Page d'utilisateurs à récupérer"
    ),
    users_size: int = Query(
        DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        alias="usersSize",
        description="Nombre d'utilisateurs par page",
    ),
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Récupère un groupe par son ID. Inclut les utilisateurs, leurs rôles et les droits du groupes sur le fournisseur de service.

    Les utilisateurs sont paginés : `users` contient la page demandée et `users_pagination` décrit la pagination.
    """
    return await group_service.get_group_with_users_and_scopes(
        group_id, users_page, users_size
    )


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
