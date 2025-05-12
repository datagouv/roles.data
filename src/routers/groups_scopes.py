# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends

from src.auth import decode_access_token
from src.dependencies import get_groups_service

from ..services.groups import GroupsService

router = APIRouter(
    prefix="/groups",
    tags=["Gestion des droits d’une équipe"],
    dependencies=[Depends(decode_access_token)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.put("/{group_id}/scopes", status_code=200)
async def create_group_scopes(
    group_id: int,
    scopes: str = "read",
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Add scopes (that apply your service provider) to a specified group
    """
    return await groups_service.add_scopes(group_id, scopes)


@router.patch("/{group_id}/scopes", status_code=200)
async def update_group_scopes(
    group_id: int,
    scopes: str = "read",
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Update scopes (that apply your service provider) to a specified group
    """
    return await groups_service.update_scopes(group_id, scopes)
