# ------- DATAPASS WEBHOOK ROUTER FILE -------

import logging

from fastapi import APIRouter, Depends

from ...dependencies import (
    get_verified_datapass_payload,
)
from ...dependencies.datapass import get_datapass_service
from ...model import (
    DataPassWebhookWrapper,
)
from ...services.datapass import DatapassService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/webhooks/datapass",
    tags=["Webhook"],
    responses={
        400: {"description": "Invalid webhook payload"},
        401: {"description": "Invalid webhook signature"},
        404: {"description": "Not found"},
        409: {"description": "Conflict - duplicate groups for contract"},
    },
)


@router.post("/")
async def receive_datapass_webhook(
    payload: DataPassWebhookWrapper = Depends(get_verified_datapass_payload),
    datapass_service: DatapassService = Depends(get_datapass_service),
):
    """
    Receive and process DataPass webhook notifications.

    This endpoint receives webhook calls from DataPass (https://datapass.api.gouv.fr)
    and automatically creates or updates groups when authorization requests are approved.

    **Authentication**: Uses HMAC SHA256 signature verification via the `X-Hub-Signature-256` header.

    **Processing Logic**:
    1. Validates webhook signature for security
    2. Checks if the event is an approval (habilitation creation) event
    3. Creates a group under the DataPass service provider if it doesn't exist
    4. Updates group scopes for the requesting service provider

    Other events are ignored and return a 200 status with "Ignored" status.
    """
    if not payload.is_demande_creating_an_habilitation:
        return {
            "status": "Ignored",
            "message": "Event does not trigger group creation or update",
            "data": {},
        }

    # Process the webhook
    group = await datapass_service.process_webhook(payload)

    return {
        "status": "Success",
        "message": "Event succesfully processed",
        "data": group,
    }
