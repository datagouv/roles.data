# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends

from ..dependencies import get_roles_service
from ..models import RoleBase, RoleResponse
from ..services.roles import RolesService

router = APIRouter(
    prefix="/roles",
    tags=["Rôles"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.post("/", response_model=RoleResponse, status_code=201)
async def create_a_new_role(
    role: RoleBase, roles_service: RolesService = Depends(get_roles_service)
):
    """
    Create a new role. Cannot create a role with the same name as an existing one.
    """
    return await roles_service.create_role(role)


@router.get("/", response_model=list[RoleResponse])
async def get_all_existing_roles(
    roles_service: RolesService = Depends(get_roles_service),
):
    """
    Retrieve all existing roles
    """
    return await roles_service.get_all_roles()


@router.get("/{role_id}", response_model=RoleResponse, status_code=200)
async def get_role_by_id(
    role_id: int, roles_service: RolesService = Depends(get_roles_service)
):
    """
    Get a role by its ID.
    """
    return await roles_service.get_roles_by_id(role_id)


@router.get("/groups/{group_id}", response_model=list[RoleResponse], status_code=200)
async def get_all_roles_for_group(
    group_id: int, roles_service: RolesService = Depends(get_roles_service)
):
    """
    Retrieve all the role currently used in a group.
    """
    return await roles_service.get_roles_for_group(group_id)
