# ------- DATAPASS WEBHOOK ROUTER FILE -------

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import get_verified_datapass_payload
from ..model import DataPassWebhookPayload

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhook"],
    responses={404: {"description": "Not found"}},
)


@router.post("/datapass")
async def receive_datapass_webhook(
    webhook_payload: DataPassWebhookPayload = Depends(get_verified_datapass_payload),
):
    """
    Receive and process DataPass webhook notifications.

    This endpoint receives webhook calls from DataPass and processes
    approval events for authorization requests.
    """
    try:
        event_type = webhook_payload.event
        state = webhook_payload.data.state

        if (
            webhook_payload.model_type
            != "authorization_request/annuaire_des_entreprises"
        ):
            """
            Can evolve into a situation where datapass tells us which ServiceProvider to use
            """
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Annuaire entreprise form are allowed yet",
            )

        is_habilitation_update = event_type == "approve" and state == "validated"

        if is_habilitation_update:
            public_id = webhook_payload.data.public_id
            return {
                "status": "success",
                "message": f"Processed {event_type} event for authorization request {public_id}",
                "event_type": event_type,
                "authorization_id": public_id,
            }

        return {
            "status": "acknowledged",
            "message": f"Received {event_type} event",
            "event_type": event_type,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing webhook: {str(e)}"
        )
