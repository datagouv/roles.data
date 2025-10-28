# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends

from src.dependencies import get_roles_service
from src.model import RoleResponse
from src.services.roles import RolesService

router = APIRouter(
    prefix="/roles",
    tags=["Rôles"],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.get("/", response_model=list[RoleResponse])
async def all(
    roles_service: RolesService = Depends(get_roles_service),
):
    """
    Retourne la liste des rôles existants.

    Les rôles ne peuvent pas être créés ou supprimés. Si vous avez besoin d’un nouveau rôle, veuillez contacter l’équipe de dev.
    """
    return await roles_service.get_all_roles()


@router.get("/{role_id}", response_model=RoleResponse, status_code=200)
async def by_id(role_id: int, roles_service: RolesService = Depends(get_roles_service)):
    """
    Récupérer un role par son ID.
    """
    return await roles_service.get_roles_by_id(role_id)
