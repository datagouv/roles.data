from fastapi import Request

from ..auth.datapass import verified_datapass_signature

# =============================
# Datapass webhook dependencies
# =============================


async def get_verified_datapass_payload(request: Request):
    """
    Dependency function that verify DataPass signature using HMAC SHA256.
    """
    body = await request.body()
    signature_header = request.headers.get("X-Hub-Signature-256")

    return await verified_datapass_signature(body, signature_header)
