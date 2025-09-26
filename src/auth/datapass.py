import hashlib
import hmac
import json

from fastapi import HTTPException, status

from src.config import settings

from ..model import DataPassWebhookPayload


async def verified_datapass_signature(
    body: bytes, signature_header: str | None
) -> DataPassWebhookPayload:
    """
    Verify DataPass signature using HMAC SHA256.

    Args:
        request: FastAPI request object containing headers and body

    Raises:
        HTTPException: If signature header is missing or signature is invalid
    """
    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Hub-Signature-256 header",
        )

    if not signature_header.startswith("sha256="):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature format"
        )

    # Extract the signature hash
    provided_signature = signature_header[7:]  # Remove "sha256=" prefix

    # Calculate expected signature
    expected_signature = hmac.new(
        settings.DATAPASS_WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256
    ).hexdigest()

    # Use secure comparison to prevent timing attacks
    if not hmac.compare_digest(provided_signature, expected_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature"
        )

    payload_dict = json.loads(body.decode("utf-8"))
    return DataPassWebhookPayload(**payload_dict)
