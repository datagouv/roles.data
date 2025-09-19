from fastapi import Depends, Request

from ..auth.datapass import verified_datapass_signature
from ..config import settings
from ..model import DataPassWebhookWrapper
from ..services.datapass import DatapassService
from .services import get_groups_service_factory

# =============================
# Datapass webhook dependencies
# =============================


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
) -> DatapassService:
    """
    Dependency function that provides a DatapassService instance.

    DataPass is the only hardcoded service provider (ID 999). It can
    create groups for other service providers.
    """
    datapass_groups_service = groups_service_factory(
        settings.DATAPASS_SERVICE_PROVIDER_ID
    )
    return DatapassService(datapass_groups_service, groups_service_factory)
