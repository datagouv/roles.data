from fastapi import Depends, Request

from ..auth.datapass import verified_datapass_signature
from ..model import DataPassWebhookWrapper
from ..services.datapass import DatapassService
from ..services.service_providers import ServiceProvidersService
from .services import get_groups_service_factory, get_service_providers_service

# =============================
# Datapass webhook dependencies
# =============================

DATAPASS_SERVICE_PROVIDER_ID = 999


async def get_verified_datapass_payload(request: Request):
    """
    Dependency function that verify DataPass signature using HMAC SHA256.
    """
    body = await request.body()
    signature_header = request.headers.get("X-Hub-Signature-256")
    verified_payload = await verified_datapass_signature(body, signature_header)
    return DataPassWebhookWrapper(verified_payload)


async def get_datapass_service(
    groups_service_factory=Depends(get_groups_service_factory),
    service_provider_service: ServiceProvidersService = Depends(
        get_service_providers_service
    ),
) -> DatapassService:
    """
    Dependency function that provides a DatapassService instance.

    DataPass is the only hardcoded service provider (ID 999). It can
    create groups for other service providers.
    """
    datapass_groups_service = groups_service_factory(DATAPASS_SERVICE_PROVIDER_ID)
    return DatapassService(
        service_provider_service, datapass_groups_service, groups_service_factory
    )
