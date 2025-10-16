# Security scheme for Bearer token extraction
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import UUID4, EmailStr

from src.auth.pro_connect import pro_connect_provider

bearer_scheme = HTTPBearer()


async def get_acting_user_from_proconnect_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> tuple[UUID4, EmailStr]:
    """
    Dependency for ProConnect Resource Server authentication.

    Extracts the Bearer token from the Authorization header, introspects it with ProConnect,
    looks up the user in the database by their ProConnect sub, and returns the acting_user_sub.
    """
    access_token = credentials.credentials

    # Introspect the token with ProConnect
    introspection_data = await pro_connect_provider.introspect_token(access_token)

    # Extract ProConnect sub from introspection response
    proconnect_sub = introspection_data.get("sub")
    proconnect_email = introspection_data.get("email")
    if not proconnect_sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain 'sub' claim",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not proconnect_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain 'email' claim",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Return the user's sub as acting_user_sub
    return (proconnect_sub, proconnect_email)
