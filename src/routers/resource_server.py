from fastapi import APIRouter, Depends, Path, Query
from pydantic import UUID4

from src.dependencies import get_groups_service
from src.dependencies.auth.pro_connect_resource_server import (
    get_acting_user_sub_from_proconnect_token,
    get_claims_from_proconnect_token,
)
from src.model import (
    GroupResponse,
    GroupWithScopesResponse,
    UserInGroupCreate,
    UserInGroupResponse,
)
from src.services.groups import GroupsService

router = APIRouter(
    prefix="/resource-server/groups",
    tags=["Gestion des groupes par l'utilisateur"],
    dependencies=[Depends(get_claims_from_proconnect_token)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.get("/", response_model=list[GroupWithScopesResponse])
async def get_my_groups(
    acting_user_sub: UUID4 = Depends(get_acting_user_sub_from_proconnect_token),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Recherche les groupes d’un utilisateur, avec son adresse e-mail et son sub ProConnect.
    """
    return await groups_service.search_groups(user_sub=acting_user_sub)


@router.put("/{group_id}", response_model=GroupResponse)
async def update_name(
    group_id: int = Path(..., description="ID du groupe"),
    group_name: str = Query(..., description="Nouveau nom"),
    acting_user_sub: UUID4 = Depends(get_acting_user_sub_from_proconnect_token),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Mise à jour du nom d'un groupe.
    """
    await groups_service.is_admin(acting_user_sub, group_id)
    return await groups_service.update_group(group_id, group_name)


@router.post("/{group_id}/users", status_code=201)
async def add_user(
    user_in_group: UserInGroupCreate,
    group_id: int = Path(..., description="ID du groupe"),
    acting_user_sub: UUID4 = Depends(get_acting_user_sub_from_proconnect_token),
    groups_service: GroupsService = Depends(get_groups_service),
) -> UserInGroupResponse:
    """
    Ajout d'un utilisateur

    Si l'utilisateur n'existe pas, il est automatiquement créé dans la base de données.

    Si le groupe ou le rôle n'existe pas, une erreur 404 sera levée.
    """
    await groups_service.is_admin(acting_user_sub, group_id)
    return await groups_service.add_user_to_group(
        group_id, user_email=user_in_group.email, role_id=user_in_group.role_id
    )


@router.patch("/{group_id}/users/{user_id}", status_code=200)
async def update_user_role(
    group_id: int = Path(..., description="ID du groupe"),
    user_id: int = Path(..., description="ID de l'utilisateur"),
    role_id: int = Query(..., description="ID du nouveau rôle"),
    acting_user_sub: UUID4 = Depends(get_acting_user_sub_from_proconnect_token),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Met à jour le rôle d'un utilisateur dans un groupe

    Si le groupe, l'utilisateur ou le rôle n'existe pas, une erreur 404 sera levée.
    """
    await groups_service.is_admin(acting_user_sub, group_id)
    return await groups_service.update_user_in_group(group_id, user_id, role_id)


@router.delete("/{group_id}/users/{user_id}", status_code=204)
async def remove_user(
    group_id: int = Path(..., description="ID du groupe"),
    user_id: int = Path(..., description="ID de l'utilisateur"),
    acting_user_sub: UUID4 = Depends(get_acting_user_sub_from_proconnect_token),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Retire un utilisateur d'un groupe.

    Si le groupe, ou l'utilisateur, une erreur 404 sera levée.
    """
    await groups_service.is_admin(acting_user_sub, group_id)
    return await groups_service.remove_user_from_group(group_id, user_id)
