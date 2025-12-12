from fastapi import APIRouter, Depends

from src.dependencies.auth.pro_connect_resource_server import (
    get_claims_from_proconnect_token,
)
from src.routers.resource_server import groups
from src.routers.resource_server import organizations

router = APIRouter(
    prefix="/resource-server",
    tags=["Gestion des ressources par l'utilisateur"],
    dependencies=[Depends(get_claims_from_proconnect_token)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)

router.include_router(groups.router)
router.include_router(organizations.router)