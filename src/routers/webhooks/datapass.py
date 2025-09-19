# ------- DATAPASS WEBHOOK ROUTER FILE -------

from fastapi import APIRouter, Depends

from ...dependencies import (
    get_verified_datapass_payload,
)
from ...dependencies.datapass import get_datapass_service
from ...model import (
    DataPassWebhookWrapper,
)
from ...services.datapass import DatapassService

router = APIRouter(
    prefix="/webhooks/datapass",
    tags=["Webhook"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def receive_datapass_webhook(
    payload: DataPassWebhookWrapper = Depends(get_verified_datapass_payload),
    datapass_service: DatapassService = Depends(get_datapass_service),
):  # -> dict[str, str] | dict[str, Any]:
    """
    Receive and process DataPass webhook notifications.

    This endpoint receives webhook calls from DataPass and processes
    approval events for authorization requests.
    """
    if not payload.is_habilitation_update:
        return {
            "status": "Ignored",
            "message": "Event does not trigger group creation or update",
            "data": {},
        }

    group = await datapass_service.process_webhook(payload)

    return {
        "status": "Success",
        "message": "Event succesfully processed",
        "data": group,
    }
