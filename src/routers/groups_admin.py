# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends, Path, Query

from src.auth import decode_access_token
from src.dependencies import get_groups_service

from ..models import GroupResponse
from ..services.groups import GroupsService

router = APIRouter(
    prefix="/groups",
    tags=["Administration d’une équipe"],
    dependencies=[Depends(decode_access_token)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.put("/{group_id}", response_model=GroupResponse)
async def update_name(
    group_id: int = Path(..., description="ID de l’équipe"),
    group_name: str = Query(..., description="Nouveau nom"),
    acting_user_sub: str = Query(
        ..., description="Sub ProConnect de l’utilisateur effectuant la requête"
    ),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Mise à jour du nom d’une équipe.
    """
    await groups_service.verify_user_is_admin(acting_user_sub, group_id)
    return await groups_service.update_group(group_id, group_name)


# Group’s users manipulation
@router.put("/{group_id}/users/{user_id}", status_code=201)
async def add_user(
    group_id: int = Path(..., description="ID de l’équipe"),
    user_id: int = Path(..., description="ID de l’utilisateur"),
    acting_user_sub: str = Query(
        ..., description="Sub ProConnect de l’utilisateur effectuant la requête"
    ),
    role_id: int = Query(..., description="ID du rôle"),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Ajout d’un utilisateur

    Si le groupe, l’utilisateur ou le rôle n’existe pas, une erreur 404 sera levée.
    """
    await groups_service.verify_user_is_admin(acting_user_sub, group_id)
    return await groups_service.add_user_to_group(group_id, user_id, role_id)


@router.patch("/{group_id}/users/{user_id}", status_code=200)
async def update_user_role(
    group_id: int = Path(..., description="ID de l’équipe"),
    user_id: int = Path(..., description="ID de l’utilisateur"),
    acting_user_sub: str = Query(
        ..., description="Sub ProConnect de l’utilisateur effectuant la requête"
    ),
    role_id: int = Query(..., description="ID du nouveau rôle"),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Met à jour le rôle d’un utilisateur dans une équipe

    Si le groupe, l’utilisateur ou le rôle n’existe pas, une erreur 404 sera levée.
    """
    await groups_service.verify_user_is_admin(acting_user_sub, group_id)
    return await groups_service.update_user_in_group(group_id, user_id, role_id)


@router.delete("/{group_id}/users/{user_id}", status_code=204)
async def remove_user(
    group_id: int = Path(..., description="ID de l’équipe"),
    user_id: int = Path(..., description="ID de l’utilisateur"),
    acting_user_sub: str = Query(
        ..., description="Sub ProConnect de l’utilisateur effectuant la requête"
    ),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Retire un utilisateur d’une équipe.

    Si le groupe, ou l’utilisateur, une erreur 404 sera levée.
    """
    await groups_service.verify_user_is_admin(acting_user_sub, group_id)
    return await groups_service.remove_user_from_group(group_id, user_id)
