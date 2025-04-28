# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends, Path, Query

from src.dependencies import get_groups_service

from ..models import GroupCreate, GroupResponse, GroupWithUsersResponse, Siren
from ..services.groups import GroupsService

router = APIRouter(
    prefix="/groups",
    tags=["Équipes"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.get("/", response_model=list[GroupResponse])
async def list_groups(
    organisation_siren: Siren = Query(None, description="Filter groups by siren"),
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    List all groups, optionally filtered by organisation siren.
    """
    return await group_service.list_groups(organisation_siren)


@router.get("/{group_id}", response_model=GroupWithUsersResponse)
async def get_group(
    group_id: int = Path(..., description="The ID of the group to retrieve"),
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Get a group by ID, including all users that belong to it.
    """
    return await group_service.get_group_with_users(group_id)


@router.post("/", response_model=GroupResponse)
async def create_group(
    group: GroupCreate,
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Create a new group.

    If the organization doesn't exist, it will be created automatically.
    """
    return await groups_service.create_group(group)


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int = Path(..., description="The ID of the group to update"),
    group_name: str = Query(..., description="The new name of the group"),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Update a group (change its name).
    """
    return await groups_service.update_group(group_id, group_name)


@router.delete("/{group_id}", status_code=204)
async def delete_group(
    group_id: int = Path(..., description="The ID of the group to delete"),
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Delete a group by ID.

    If delete_orphaned_orga is True and the organization has no groups left after deletion,
    the organization will also be deleted.
    """
    return await group_service.delete_group(group_id)


# Group’s users manipulation


@router.post("/{group_id}/users/{user_id}", status_code=201)
async def add_user_to_group(
    group_id: int = Path(..., description="The ID of the group"),
    user_id: int = Path(..., description="The ID of the user"),
    role_id: int = Query(..., description="The ID of the user's role"),
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Add a user to a given group with a specific role.

    If the group, the user or the role does not exist, a 404 error will be raised.
    """
    return await group_service.add_user_to_group(group_id, user_id, role_id)


@router.delete("/{group_id}/users/{user_id}", status_code=204)
async def remove_user_from_group(
    group_id: int = Path(..., description="The ID of the group"),
    user_id: int = Path(..., description="The ID of the user"),
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Remove a user from a given group

    If the group or the user does not exist, a 404 error will be raised.
    """
    return await group_service.remove_user_from_group(group_id, user_id)


@router.put("/{group_id}/users/{user_id}", status_code=200)
async def update_user_role_in_group(
    group_id: int = Path(..., description="The ID of the group"),
    user_id: int = Path(..., description="The ID of the user"),
    role_id: str = Query(..., description="User role"),
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Update user role a user from a given group
    """
    return await group_service.delete_group(group_id)
