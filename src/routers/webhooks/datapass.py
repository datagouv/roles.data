# ------- DATAPASS WEBHOOK ROUTER FILE -------

from fastapi import APIRouter, Depends
from pydantic import HttpUrl

from ...dependencies import (
    get_service_providers_service,
    get_verified_datapass_payload,
    get_webhook_groups_service_factory,
)
from ...model import DataPassWebhookPayload, GroupCreate, UserCreate
from ...services.services_provider import ServiceProvidersService

router = APIRouter(
    prefix="/webhooks/datapass",
    tags=["Webhook"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def receive_datapass_webhook(
    webhook_payload: DataPassWebhookPayload = Depends(get_verified_datapass_payload),
    groups_service_factory=Depends(get_webhook_groups_service_factory),
    service_providers_service: ServiceProvidersService = Depends(
        get_service_providers_service
    ),
):  # -> dict[str, str] | dict[str, Any]:
    """
    Receive and process DataPass webhook notifications.

    This endpoint receives webhook calls from DataPass and processes
    approval events for authorization requests.
    """
    event_type = webhook_payload.event
    state = webhook_payload.data.state
    public_id = webhook_payload.data.public_id

    attempted_service_provider_id = (
        1
        if webhook_payload.model_type
        == "authorization_request/annuaire_des_entreprises"
        else -1
    )
    service_provider = await service_providers_service.get_service_provider_by_id(
        attempted_service_provider_id
    )

    is_habilitation_update = event_type == "approve" and state == "validated"

    if not is_habilitation_update:
        return {
            "status": "Ignored",
            "message": f"{event_type} - {state} does not trigger group creation or update",
        }

    group_data = GroupCreate(
        name=webhook_payload.data.data.intitule,
        organisation_siret=webhook_payload.data.organization.siret,
        admin=UserCreate(
            email=webhook_payload.data.applicant.email,
        ),
        scopes=f"{public_id}",
        contract_description=f"DEMANDE_{public_id}",
        contract_url=HttpUrl(f"https://datapass.api.gouv.fr/demandes/{public_id}"),
    )

    # Create group for datapass service provider
    datapass_groups_service = await groups_service_factory(
        99
    )  # DataPass service provider ID = 99
    created_group = await datapass_groups_service.create_group(group_data)

    # Add the same group to datapass service provider
    service_provider_group_service = await groups_service_factory(
        service_provider.id
    )  # Annuaire service provider ID = 1
    await service_provider_group_service.add_relation(
        created_group.id,
        " ".join(webhook_payload.data.data.scopes),
        f"DATAPASS_{public_id}",
        HttpUrl(f"https://datapass.api.gouv.fr/demandes/{public_id}"),
    )

    return {
        "status": "Success",
        "message": f"Group {created_group.id} created",
    }
