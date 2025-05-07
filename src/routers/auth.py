# ------- USER ROUTER FILE -------
from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.auth import create_access_token
from src.dependencies import get_auth_service
from src.models import Token
from src.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)

ACCESS_TOKEN_EXPIRE_MINUTES = 60


# Add this in your auth router
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    service_account = await auth_service.authenticate(
        client_id=form_data.username, client_secret=form_data.password
    )

    # Create access token with the authorized service provider id embedded
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"service_provider_id": service_account.service_provider_id},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}
