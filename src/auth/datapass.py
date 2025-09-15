import hashlib
import hmac

from fastapi import HTTPException
from fastapi.datastructures import Headers

from src.config import settings


async def verify_datapass_signature(body: bytes, headers: Headers) -> None:
    """
    Verify DataPass signature using HMAC SHA256.

    Args:
        request: FastAPI request object containing headers and body

    Raises:
        HTTPException: If signature header is missing or signature is invalid
    """
    signature_header = headers.get("X-Hub-Signature-256")

    if not signature_header:
        raise HTTPException(
            status_code=400, detail="Missing X-Hub-Signature-256 header"
        )

    if not signature_header.startswith("sha256="):
        raise HTTPException(status_code=400, detail="Invalid signature format")

    # Extract the signature hash
    provided_signature = signature_header[7:]  # Remove "sha256=" prefix

    # Calculate expected signature
    expected_signature = hmac.new(
        settings.DATAPASS_WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256
    ).hexdigest()

    # Use secure comparison to prevent timing attacks
    if not hmac.compare_digest(provided_signature, expected_signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
