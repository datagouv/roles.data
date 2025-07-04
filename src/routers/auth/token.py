import base64

from fastapi import APIRouter, Depends, Form, Header, HTTPException, Request, status

from src.auth import create_access_token
from src.config import settings
from src.dependencies import get_auth_service
from src.model import Token
from src.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.post("/token", response_model=Token)
async def get_token(
    request: Request,
    authorization: str | None = Header(None),
    grant_type: str = Form(...),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    OAuth2 pour un flow “Client Credentials”.

    L’authentication peut être effectuée de deux manières :
    1. HTTP Basic Authentication dans le header Authorization
    2. `client_id` et `client_secret` dans le body de la requête (form data)

    Le `grant_type` est `client_credentials`.
    """
    # Verify grant type
    if grant_type != "client_credentials":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported grant type. Only 'client_credentials' is supported.",
        )

    client_id = None
    client_secret = None

    # Method 1: Extract from HTTP Basic Auth header
    if authorization and authorization.startswith("Basic "):
        try:
            # Extract and decode the base64 credentials
            auth_decoded = base64.b64decode(authorization.split(" ")[1]).decode("utf-8")
            client_id, client_secret = auth_decoded.split(":", 1)
        except Exception:
            pass  # If Basic auth parsing fails, try form data

    # Method 2: Try to get from form data if not in Basic Auth
    if not client_id or not client_secret:
        form = await request.form()
        client_id = form.get("client_id")
        client_secret = form.get("client_secret")

    # Ensure we have both credentials
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Client authentication required",
            headers={"WWW-Authenticate": "Basic realm='OAuth2 Client Authentication'"},
        )

    try:
        # Authenticate client
        service_account = await auth_service.authenticate(
            client_id=str(client_id), client_secret=str(client_secret)
        )

        # Create access token with the service provider ID and requested scope
        token_data = {
            "service_provider_id": service_account.service_provider_id,
            "service_account_id": service_account.id,
        }
        access_token = create_access_token(data=token_data)

        # Return the access token in OAuth2-compliant format
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.API_ACCESS_TOKEN_EXPIRE_MINUTES
            * 60,  # 1 hour in seconds
        }

    except HTTPException as e:
        # Re-raise authentication errors
        raise e
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}",
        )
