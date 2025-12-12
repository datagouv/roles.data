from fastapi import APIRouter, Depends

from src.dependencies import get_groups_service
from src.dependencies.auth.pro_connect_resource_server import (
    get_acting_user_organization_siret_from_proconnect_token,
)
from src.model import (
    OrganisationGroupResponse,
    Siret,
)
from src.services.groups import GroupsService

router = APIRouter(
    prefix="/organizations",
    tags=["Gestion des organisations par l'utilisateur"],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.get("/groups", response_model=list[OrganisationGroupResponse])
async def get_my_groups(
    acting_user_organization_siret: Siret = Depends(get_acting_user_organization_siret_from_proconnect_token),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Recherche les groupes d'une organisation, avec son SIRET.
    """
    return await groups_service.search_groups_by_organisation_siret(siret=acting_user_organization_siret)
