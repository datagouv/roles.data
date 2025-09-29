import hashlib
import hmac
import json
from random import randint

from src.config import settings


def create_webhook_signature(payload_bytes: bytes) -> str:
    """Create HMAC SHA256 signature for webhook payload."""
    signature = hmac.new(
        settings.DATAPASS_WEBHOOK_SECRET.encode("utf-8"), payload_bytes, hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


def submit_datapass_webhook(
    client, payload: dict, service_provider_id: int = 1, environment: str = "sandbox"
):
    payload_bytes = json.dumps(payload).encode("utf-8")
    signature = create_webhook_signature(payload_bytes)

    return client.post(
        f"/webhooks/datapass?service_provider_id={service_provider_id}",
        content=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": signature,
            "X-App-Environment": environment,
        },
    )


def create_datapass_payload(
    event: str = "approve",
    state: str = "validated",
    intitule: str = "Ma demande",
    applicant_email: str = "jean.dupont@beta.gouv.fr",
    scopes: list[str] = [],
) -> dict:
    """
    Create a parametrized DataPass webhook payload for testing.

    See https://github.com/etalab/data_pass/blob/develop/docs/webhooks.md
    """

    return {
        "event": event,
        "fired_at": 1628253953,
        "model_type": "authorization_request/annuaire_des_entreprises",
        "data": {
            "id": randint(1, 7000),
            "public_id": "a90939e8-f906-4343-8996-5955257f161d",
            "state": state,
            "form_uid": "api-entreprise-demande-libre",
            "organization": {
                "id": 9002,
                "name": "UMAD CORP",
                "siret": "98043033400022",
            },
            "applicant": {
                "id": 9003,
                "email": applicant_email,
                "given_name": "Jean",
                "family_name": "Dupont",
                "phone_number": "0836656565",
                "job_title": "Rockstar",
            },
            "data": {
                "intitule": intitule,
                "scopes": scopes,
            },
        },
    }


# ============
# Test authent
# ============


def test_datapass_webhook_invalid_signature(client):
    """Test DataPass webhook with invalid signature."""
    payload = create_datapass_payload(event="approve", state="validated")

    payload_bytes = json.dumps(payload).encode("utf-8")

    response = client.post(
        "/webhooks/datapass?service_provider_id=1",
        content=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=invalid_signature_here",
            "X-App-Environment": "sandbox",
        },
    )

    assert response.status_code == 401
    assert "Invalid webhook signature" in response.json()["detail"]


def test_datapass_webhook_missing_signature(client):
    """Test DataPass webhook with missing signature header."""
    payload = create_datapass_payload(event="approve", state="validated")

    payload_bytes = json.dumps(payload).encode("utf-8")

    response = client.post(
        "/webhooks/datapass?service_provider_id=1",
        content=payload_bytes,
        headers={"Content-Type": "application/json", "X-App-Environment": "sandbox"},
    )

    assert response.status_code == 401
    assert "Missing X-Hub-Signature-256 header" in response.json()["detail"]


def test_datapass_webhook_missing_service_provider_id(client):
    """Test DataPass webhook with missing service_provider_id query parameter."""
    payload = create_datapass_payload(event="approve", state="validated")
    payload_bytes = json.dumps(payload).encode("utf-8")
    signature = create_webhook_signature(payload_bytes)

    response = client.post(
        "/webhooks/datapass",  # Missing service_provider_id query param
        content=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": signature,
            "X-App-Environment": "sandbox",
        },
    )

    assert response.status_code == 422  # FastAPI validation error
    assert "Field required" in response.json()["detail"][0]["msg"]


# =======================
# Test payload processing
# =======================


def test_datapass_webhook_refuse_event(client):
    """Test DataPass webhook with refuse event."""
    payload = create_datapass_payload(event="refuse", state="refused")
    response = submit_datapass_webhook(client, payload)

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "Ignored"
    assert "does not trigger group creation" in json_response["message"]


def test_datapass_webhook_nonexistent_service_provider(client):
    """Test DataPass webhook with non-existent service provider."""
    impossible_service_provider_id = 88888
    payload = create_datapass_payload(
        event="approve",
        state="validated",
    )
    response = submit_datapass_webhook(
        client, payload, service_provider_id=impossible_service_provider_id
    )

    assert response.status_code == 404
    assert "Service provider not found" in response.json()["detail"]


def test_datapass_webhook_existing_habilitation_scope_update(client):
    """Test DataPass webhook updates scopes for existing habilitation."""
    applicant_email = "existing.admin@test.gouv.fr"
    intitule = "demande pour mes amis"
    initial_scopes = ["initial_scope1", "initial_scope2"]

    # First, create an initial habilitation for the TEST service provider (ID = 1)
    initial_payload = create_datapass_payload(
        event="approve",
        state="validated",
        intitule=intitule,
        applicant_email=applicant_email,
        scopes=initial_scopes,
    )

    initial_response = submit_datapass_webhook(
        client, initial_payload, service_provider_id=1
    )

    assert initial_response.status_code == 200
    initial_json = initial_response.json()
    assert initial_json["status"] == "Success"
    assert initial_json["message"] == "Event succesfully processed"

    # Get the created group ID
    initial_group_data = initial_json["data"]
    group_id = initial_group_data["id"]

    # Since DataPass creates groups, we need to check the target service provider (ID=1) for the relation
    groups_response = client.get(f"/groups/{group_id}")
    assert groups_response.status_code == 200
    group = groups_response.json()
    assert group["scopes"] == " ".join(initial_scopes)
    assert group["name"] == f"Groupe {intitule}"
    assert group["contract_description"] == initial_payload["data"]["form_uid"]
    assert group["users"][0]["email"] == applicant_email

    # First, simulate an habilitation update
    updated_scopes = ["updated_scope1", "updated_scope2", "new_scope3"]
    initial_payload["data"]["data"]["scopes"] = updated_scopes
    submit_datapass_webhook(client, initial_payload, service_provider_id=1)

    groups_response = client.get(f"/groups/{group_id}")
    assert groups_response.status_code == 200
    group = groups_response.json()
    assert group["scopes"] == " ".join(updated_scopes)
