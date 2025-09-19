# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends, Query
from pydantic import HttpUrl

from src.auth.o_auth import decode_access_token
from src.dependencies import get_groups_service

from ..services.groups import GroupsService

router = APIRouter(
    prefix="/groups",
    tags=["Gestion des droits d’un groupe"],
    dependencies=[Depends(decode_access_token)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.patch("/{group_id}/scopes", status_code=200)
async def update_group_scopes(
    group_id: int,
    scopes: str = Query(
        "",
        description="Liste des scopes (facultatif)",
    ),
    contract_description: str = Query(
        None,
        description="Description du contrat (facultatif)",
    ),
    contract_url: HttpUrl = Query(
        None,
        description="Url du contrat (facultatif)",
    ),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Met à jour :
    - les droits ou `scopes` d’un groupe sur votre fournisseur de service
    - le contrat qui lie le groupe à votre fournisseur de service
    """
    return await groups_service.update_or_create_scopes(
        group_id,
        scopes,
        contract_description,
        contract_url,
    )
