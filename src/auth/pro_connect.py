import jwt
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client.apps import StarletteOAuth2App

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


pro_connect_provider = ProConnectOAuthProvider(settings)
