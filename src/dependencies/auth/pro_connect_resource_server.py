# Security scheme for Bearer token extraction
from fastapi import Depends, HTTPException, status
from pydantic import UUID4, EmailStr

from .pro_connect import pro_connect_provider
from .pro_connect_bearer_token import decode_proconnect_bearer_token


async def get_claims_from_proconnect_token(
    proconnect_access_token=Depends(decode_proconnect_bearer_token),
) -> tuple[UUID4, EmailStr, str]:
    """
    ProConnect Resource Server authentication - supports both direct call and dependency injection.

    Returns:
        Tuple of (proconnect_sub, proconnect_email, client_id)

    Usage:
        As dependency: Depends(get_claims_from_proconnect_token)
        Direct call: await get_claims_from_proconnect_token(credentials=token_string)
    """
    introspection_data = await pro_connect_provider.introspect_token(
        proconnect_access_token
    )

    for claim in ["sub", "email", "client_id"]:
        if not introspection_data.get(claim):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token does not contain '{claim}' claim",
                headers={"WWW-Authenticate": "Bearer"},
            )

    proconnect_sub: UUID4 = introspection_data.get("sub")  # type: ignore
    proconnect_email: EmailStr = introspection_data.get("email")  # type: ignore
    client_id: str = introspection_data.get("client_id")  # type: ignore

    return (proconnect_sub, proconnect_email, client_id)


async def get_acting_user_sub_from_proconnect_token(
    proconnect_claims=Depends(get_claims_from_proconnect_token),
):
    acting_user_sub, _, _ = proconnect_claims
    return acting_user_sub
