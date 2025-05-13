# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends, Path, Query
from pydantic import EmailStr

from src.auth import decode_access_token
from src.dependencies import get_groups_service

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
    List every available groups for your service provider
    """
    return await group_service.list_groups()


@router.get("/search", response_model=list[GroupWithUsersAndScopesResponse])
async def search_groups_by_user(
    email: EmailStr = Query(
        ..., description="The email of the user to filter groups by"
    ),
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Search for groups by user email.
    """
    return await group_service.search_groups(email=email)


@router.get("/{group_id}", response_model=GroupWithUsersAndScopesResponse)
async def get_group(
    group_id: int = Path(..., description="The ID of the group to retrieve"),
    group_service: GroupsService = Depends(get_groups_service),
):
    """
    Get a group by ID, including all users that belong to it.
    """
    return await group_service.get_group_with_users_and_scopes(group_id)


@router.post("/", response_model=GroupResponse, status_code=201)
async def create_group(
    group: GroupCreate,
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Create a new group.

    If the organization doesn't exist, it will be created automatically.
    """
    return await groups_service.create_group(group)


@router.put("/{group_id}/scopes", status_code=200)
async def add_scopes_to_an_existing_group(
    group_id: int,
    scopes: str = "read",
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Add scopes (that apply your service provider) to a specified group

    Can only be applied to a public group
    """
    return await groups_service.add_scopes(group_id, scopes)


@router.patch("/{group_id}/scopes", status_code=200)
async def update_existing_group_scopes(
    group_id: int,
    scopes: str = "read",
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Update scopes (that apply your service provider) to a specified group
    """
    return await groups_service.update_scopes(group_id, scopes)
