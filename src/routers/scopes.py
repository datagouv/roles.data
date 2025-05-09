# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends

from src.auth import decode_access_token
from src.dependencies import get_groups_service

from ..services.groups import GroupsService

router = APIRouter(
    prefix="/scopes",
    tags=["Scopes"],
    dependencies=[Depends(decode_access_token)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.put("/{group_id}", status_code=200)
async def grant_access(
    group_id: int,
    scopes: str = "read",
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Grant scopes for a given group to your service provider
    """
    return await group_service.grant_access(group_id, scopes)


@router.patch("/{group_id}", status_code=200)
async def update_access(
    group_id: int,
    scopes: str = "read",
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Update scopes for a given group on your service provider
    """
    return await group_service.update_access(group_id, scopes)
