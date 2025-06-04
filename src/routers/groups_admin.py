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
async def update_group(
    group_id: int = Path(..., description="The ID of the group to update"),
    group_name: str = Query(..., description="The new name of the group"),
    active_user_sub: str = Query(
        ..., description="The ProConnect sub of the user making the request"
    ),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Update a group (change its name).
    """
    await groups_service.verify_user_is_admin(active_user_sub, group_id)
    return await groups_service.update_group(group_id, group_name)


# Group’s users manipulation
@router.put("/{group_id}/users/{user_id}", status_code=201)
async def add_user_to_group(
    group_id: int = Path(..., description="The ID of the group"),
    user_id: int = Path(..., description="The ID of the user"),
    admin_id: int = Query(
        ..., description="The user ID of the admin making the request"
    ),
    role_id: int = Query(..., description="The ID of the user's role"),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Add a user to a given group with a specific role.

    If the group, the user or the role does not exist, a 404 error will be raised.
    """
    await groups_service.verify_user_is_admin(admin_id, group_id)
    return await groups_service.add_user_to_group(group_id, user_id, role_id)


@router.patch("/{group_id}/users/{user_id}", status_code=200)
async def update_user_role_in_group(
    group_id: int = Path(..., description="The ID of the group"),
    user_id: int = Path(..., description="The ID of the user"),
    admin_id: int = Query(
        ..., description="The user ID of the admin making the request"
    ),
    role_id: int = Query(..., description="The ID of the role"),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Update the role of a user in a specified group.
    """
    await groups_service.verify_user_is_admin(admin_id, group_id)
    return await groups_service.update_user_in_group(group_id, user_id, role_id)


@router.delete("/{group_id}/users/{user_id}", status_code=204)
async def remove_user_from_group(
    group_id: int = Path(..., description="The ID of the group"),
    user_id: int = Path(..., description="The ID of the user"),
    admin_id: int = Query(
        ..., description="The user ID of the admin making the request"
    ),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Remove a user from a given group

    If the group or the user does not exist, a 404 error will be raised.
    """
    await groups_service.verify_user_is_admin(admin_id, group_id)
    return await groups_service.remove_user_from_group(group_id, user_id)
