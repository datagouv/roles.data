# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends

from src.auth import decode_access_token

from ..dependencies import get_roles_service
from ..models import RoleResponse
from ..services.roles import RolesService

router = APIRouter(
    prefix="/roles",
    tags=["Rôles"],
    dependencies=[Depends(decode_access_token)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


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
