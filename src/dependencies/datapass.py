from fastapi import Depends, Request

from ..config import settings
from ..model import DataPassWebhookWrapper
from ..services.datapass import DatapassService
from .auth.datapass import verified_datapass_signature
from .email import get_email_service
from .services import get_groups_service_factory, get_users_service

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
    # sandbox, staging, prod
    datapass_env = request.headers.get("X-App-Environment")

    return DataPassWebhookWrapper(verified_payload, datapass_env)


async def get_datapass_service(
    groups_service_factory=Depends(get_groups_service_factory),
    email_service=Depends(get_email_service),
    user_service=Depends(get_users_service),
) -> DatapassService:
    """
    Dependency function that provides a DatapassService instance.

    DataPass is the only hardcoded service provider (ID 999). It can
    create groups for other service providers.
    """
    datapass_groups_service = groups_service_factory(
        settings.DATAPASS_SERVICE_PROVIDER_ID, should_send_emails=False
    )
    return DatapassService(
        datapass_groups_service, groups_service_factory, email_service, user_service
    )
