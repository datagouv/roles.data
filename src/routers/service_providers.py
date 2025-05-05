# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends

from ..dependencies import get_users_service
from ..models import UserResponse
from ..services.users import UsersService

router = APIRouter(
    prefix="/service-providers",
    tags=["Fournisseurs de services"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.get("/{service_provider_id}", status_code=200)
async def get_service_provider_by_id(
    service_provider_id: int, users_service: UsersService = Depends(get_users_service)
):
    """
    Get a service provider by ID.
    """
    pass


@router.post("/{service_provider_id}/groups/{group_id}", response_model=UserResponse)
async def grant_service_access_to_group(
    service_provider_id: int,
    group_id: int,
    users_service: UsersService = Depends(get_users_service),
):
    """
    Get a specific user by email, including all roles and group memberships.
    """
    pass
