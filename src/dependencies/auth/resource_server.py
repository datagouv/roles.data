# Security scheme for Bearer token extraction
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import UUID4, EmailStr

from ..auth.pro_connect import pro_connect_provider

bearer_scheme = HTTPBearer()


async def get_claims_from_proconnect_token(
    credentials: HTTPAuthorizationCredentials | str = Depends(bearer_scheme),
) -> tuple[UUID4, EmailStr, str]:
    """
    ProConnect Resource Server authentication - supports both direct call and dependency injection.

        Args:
        credentials: Either HTTPAuthorizationCredentials (when used as FastAPI dependency)
                    or a token string (when called directly from get_request_context)

    Returns:
        Tuple of (proconnect_sub, proconnect_email, client_id)

    Usage:
        As dependency: Depends(get_claims_from_proconnect_token)
        Direct call: await get_claims_from_proconnect_token(credentials=token_string)
    """
    # Support both token string and HTTPAuthorizationCredentials
    if isinstance(credentials, str):
        access_token = credentials
    else:
        access_token = credentials.credentials

    # Introspect the token with ProConnect
    introspection_data = await pro_connect_provider.introspect_token(access_token)

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


def proconnect_resource_server(router):
    """
    Indicate that the router uses ProConnect resource server authentication
    """
    router._is_proconnect_resource_server = True
    return router


def is_resource_server(request: Request) -> bool:
    """
    Check if the current route is marked as a ProConnect resource server route.
    """
    route = request.scope.get("route")

    if route:
        if hasattr(route, "dependant") and hasattr(route.dependant, "call"):
            call = route.dependant.call
            if getattr(call, "_is_proconnect_resource_server", False):
                return True

    return False
