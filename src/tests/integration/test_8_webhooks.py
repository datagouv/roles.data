import hashlib
import hmac
import json

from src.config import settings


def create_webhook_signature(payload_bytes: bytes) -> str:
    """Create HMAC SHA256 signature for webhook payload."""
    signature = hmac.new(
        settings.DATAPASS_WEBHOOK_SECRET.encode("utf-8"), payload_bytes, hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


def create_datapass_payload(event: str = "approve", state: str = "validated") -> dict:
    """Create a parametrized DataPass webhook payload for testing."""
    return {
        "event": event,
        "fired_at": 1628253953,
        "model_type": "authorization_request/annuaire_des_entreprises",
        "data": {
            "id": 9001,
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
                "email": "jean.dupont@beta.gouv.fr",
                "given_name": "Jean",
                "family_name": "Dupont",
                "phone_number": "0836656565",
                "job_title": "Rockstar",
            },
            "data": {
                "intitule": "Ma demande",
                "scopes": ["cnaf_identite", "cnaf_enfants"],
                "contact_technique_given_name": "Tech",
                "contact_technique_family_name": "Os",
                "contact_technique_phone_number": "08366666666",
                "contact_technique_job_title": "DSI",
                "contact_technique_email": "tech@beta.gouv.fr",
            },
        },
    }


def test_datapass_webhook_approve_event(client):
    """Test DataPass webhook with approve event."""
    payload = create_datapass_payload(event="approve", state="validated")

    payload_bytes = json.dumps(payload).encode("utf-8")
    signature = create_webhook_signature(payload_bytes)

    response = client.post(
        "/webhooks/datapass",
        content=payload_bytes,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": signature},
    )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "success"
    assert json_response["event_type"] == "approve"
    assert json_response["authorization_id"] == "a90939e8-f906-4343-8996-5955257f161d"


def test_datapass_webhook_refuse_event(client):
    """Test DataPass webhook with refuse event."""
    payload = create_datapass_payload(event="refuse", state="refused")

    payload_bytes = json.dumps(payload).encode("utf-8")
    signature = create_webhook_signature(payload_bytes)

    response = client.post(
        "/webhooks/datapass",
        content=payload_bytes,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": signature},
    )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "acknowledged"
    assert json_response["event_type"] == "refuse"


def test_datapass_webhook_invalid_signature(client):
    """Test DataPass webhook with invalid signature."""
    payload = create_datapass_payload(event="approve", state="validated")

    payload_bytes = json.dumps(payload).encode("utf-8")

    response = client.post(
        "/webhooks/datapass",
        content=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=invalid_signature_here",
        },
    )

    assert response.status_code == 401
    assert "Invalid webhook signature" in response.json()["detail"]


def test_datapass_webhook_missing_signature(client):
    """Test DataPass webhook with missing signature header."""
    payload = create_datapass_payload(event="approve", state="validated")

    payload_bytes = json.dumps(payload).encode("utf-8")

    response = client.post(
        "/webhooks/datapass",
        content=payload_bytes,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 401
    assert "Missing X-Hub-Signature-256 header" in response.json()["detail"]
