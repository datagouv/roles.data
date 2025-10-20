from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jwt.exceptions import InvalidTokenError

from src.config import settings


class OAuth2ClientCredentials(OAuth2):
    """
    Custom OAuth2 security class for Client Credentials flow.

    This security scheme uses Bearer tokens and follows the Client Credentials
    OAuth2 specification.
    """

    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str | None = None,
        scopes: dict[str, str] | None = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = {
            "clientCredentials": {
                "tokenUrl": tokenUrl,
                "scopes": scopes,
            }
        }
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> str | None:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None

        return param


# Initialize the custom OAuth2 security scheme
oauth2_scheme = OAuth2ClientCredentials(
    tokenUrl="/auth/token",
    scopes={},
)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.API_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.API_SECRET_KEY, algorithm=settings.API_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token, settings.API_SECRET_KEY, algorithms=[settings.API_ALGORITHM]
        )
        return payload
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
