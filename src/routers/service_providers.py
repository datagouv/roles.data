# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends

from auth.o_auth import decode_access_token
from model import ServiceProviderResponse
from src.services.services_provider import ServiceProvidersService

from ..dependencies import (
    get_service_account_provider_pair,
    get_service_providers_service,
)
from ..model import ServiceAccountProviderPair

router = APIRouter(
    prefix="/service-providers",
    tags=["Fournisseur de services"],
    dependencies=[Depends(decode_access_token)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.get("/info", status_code=200)
async def get_service_provider_info(
    service_account_provider_pair: ServiceAccountProviderPair = Depends(
        get_service_account_provider_pair
    ),
    service_providers_service: ServiceProvidersService = Depends(
        get_service_providers_service
    ),
) -> ServiceProviderResponse:
    """
    Récupère les informations du fournisseur de service associé au compte de service.
    """
    return await service_providers_service.get_service_provider_by_id(
        service_account_provider_pair.service_provider_id
    )
