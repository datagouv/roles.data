# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends

from src.auth import decode_access_token
from src.services.services_provider import ServiceProvidersService

from ..dependencies import get_service_provider_id, get_service_providers_service

router = APIRouter(
    prefix="/service-providers",
    tags=["Fournisseurs de services"],
    dependencies=[Depends(decode_access_token)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.get("/", status_code=200)
async def get_all_service_providers(
    service_providers_service: ServiceProvidersService = Depends(
        get_service_providers_service
    ),
):
    """
    List of all service providers.
    """
    return await service_providers_service.get_all_service_providers()


@router.get("/info", status_code=200)
async def get_service_provider_info(
    service_provider_id: int = Depends(get_service_provider_id),
    service_providers_service: ServiceProvidersService = Depends(
        get_service_providers_service
    ),
):
    """
    Get the details of the service provider paired with your service account.
    """
    return await service_providers_service.get_service_provider_by_id(
        service_provider_id
    )
