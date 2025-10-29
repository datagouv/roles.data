import jwt
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client.apps import StarletteOAuth2App
from fastapi import HTTPException, status

from src.config import AppSettings, settings


class ProConnectOAuthProvider(OAuth):
    def __init__(self, settings: AppSettings):
        super().__init__()
        self.register(
            name="proconnect",
            client_id=settings.PROCONNECT_CLIENT_ID,
            client_secret=settings.PROCONNECT_CLIENT_SECRET,
            server_metadata_url=settings.PROCONNECT_URL_DISCOVER,
            redirect_uri=settings.PROCONNECT_REDIRECT_URI,
            post_logout_redirect_uri=settings.PROCONNECT_POST_LOGOUT_REDIRECT_URI,
            client_kwargs={"scope": "openid email"},
        )

    @property
    def proconnect(self) -> "StarletteOAuth2App":
        """Type hint for the proconnect client"""
        return self._clients["proconnect"]

    async def userinfo(self, token):
        """
        Custom userinfo method that handles JWT response
        NB : there is an authlib method for this, but it expects a json when PC returns a JWT (text).
        """
        try:
            metadata = await self.proconnect.load_server_metadata()
            userinfo_endpoint = metadata["userinfo_endpoint"]

            resp = await self.proconnect.get(
                userinfo_endpoint, token=token, headers={"Accept": "application/jwt"}
            )

            if resp.status_code != 200:
                raise Exception(f"Failed to get userinfo: {resp.status_code}")

            userinfo_jwt = resp.text
            header = jwt.get_unverified_header(userinfo_jwt)

            if header.get("alg") != "RS256":
                raise ValueError(f"Expected RS256, got {header.get('alg')}")

            return jwt.decode(userinfo_jwt, options={"verify_signature": False})
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"UserInfo error: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def introspect_token(self, access_token: str) -> dict:
        """
        Introspect a ProConnect access token to validate it and get user info.

        This combines token introspection (for validation) with userinfo (for claims).

        Args:
            access_token: The access token to introspect

        Returns:
            Combined dict with introspection data and user claims (sub, email)
        """
        try:
            metadata = await self.proconnect.load_server_metadata()
            introspection_endpoint = metadata.get("introspection_endpoint")

            if not introspection_endpoint:
                raise Exception(
                    "ProConnect introspection endpoint not found in metadata"
                )

            response = await self.proconnect.post(
                introspection_endpoint,
                token=access_token,
                data={
                    "token": access_token,
                    "token_type_hint": "access_token",
                },
                auth=(
                    self.proconnect.client_id,
                    self.proconnect.client_secret,
                ),
            )

            if response.status_code != 200:
                raise Exception(f"Token introspection failed: {response.status_code}")

            introspection_data = response.json()

            if not introspection_data.get("active", False):
                raise Exception("Token is not active or has expired")

            for claim in ["sub", "client_id"]:
                if not introspection_data.get(claim):
                    raise Exception(f"Token does not contain '{claim}' claim")

            return {
                "sub": introspection_data["sub"],
                "client_id": introspection_data["client_id"],
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token introspection error: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )


pro_connect_provider = ProConnectOAuthProvider(settings)
