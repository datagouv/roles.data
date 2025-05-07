# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends, Path

from src.services.services_provider import ServiceProvidersService

from ..dependencies import get_service_providers_service

router = APIRouter(
    prefix="/service-providers",
    tags=["Fournisseurs de services"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.get("/{service_provider_id}", status_code=200)
async def get_service_provider_by_id(
    service_provider_id: int = Path(
        ..., description="The ID of the service provider to retrieve"
    ),
    service_providers_service: ServiceProvidersService = Depends(
        get_service_providers_service
    ),
):
    """
    Get a service provider by ID.
    """
    return await service_providers_service.get_service_provider_by_id(
        service_provider_id
    )
