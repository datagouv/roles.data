import secrets

# Typing ProConnectOAuth
from typing import TYPE_CHECKING
from urllib.parse import urlencode

import jwt
from authlib.integrations.starlette_client import OAuth, OAuthError
from authlib.integrations.starlette_client.apps import StarletteOAuth2App
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from src.config import Settings, settings

if TYPE_CHECKING:
    from authlib.integrations.starlette_client.apps import StarletteOAuth2App


# This is a router for ProConnect authentication
# It handles login, callback, and logout functionality
# It uses OAuth2 with OpenID Connect to authenticate users via ProConnect

# It is not the same as the main auth router and is only useful for web interfaces

router = APIRouter(
    prefix="/auth/pro-connect",
    responses={404: {"description": "Not found"}},
)


class ProConnectOAuth(OAuth):
    def __init__(self, settings: Settings):
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


oauth = ProConnectOAuth(Settings())


@router.get("/login")
async def login(request: Request):
    """Redirect to ProConnect login"""
    redirect_uri = request.url_for("callback")
    authorize_url = await oauth.proconnect.authorize_redirect(
        request, redirect_uri, acr_values="eidas1"
    )
    return authorize_url


@router.get("/callback")
async def callback(request: Request):
    """Create session and actual login after ProConnect callback"""
    try:
        token = await oauth.proconnect.authorize_access_token(request)

        # Store the user info in the session, it'll be used when logging out from ProConnect.
        request.session["id_token"] = token["id_token"]
        userinfo = await oauth.userinfo(token=token)
        request.session["user"] = {
            "email": userinfo["email"],
            "name": userinfo.get("name", "Unknown"),
        }

        return RedirectResponse(url="/admin", status_code=302)

    except OAuthError as e:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=f"OAuth error: {str(e)}"
        )


@router.get("/logout")
async def logout(request: Request):
    """Logout from ProConnect"""
    id_token = request.session["id_token"]

    # Redirect to ProConnect logout
    metadata = await oauth.proconnect.load_server_metadata()
    logout_url = metadata["end_session_endpoint"]
    post_logout_redirect_uri = settings.PROCONNECT_POST_LOGOUT_REDIRECT_URI

    state = secrets.token_urlsafe(32)
    request.session["state"] = state

    logout_params = {
        "post_logout_redirect_uri": post_logout_redirect_uri,
        "id_token_hint": id_token,
        "state": state,
    }

    return RedirectResponse(
        url=f"{logout_url}?{urlencode(logout_params)}", status_code=302
    )


@router.get("/logout-callback")
async def logout_callback(request: Request):
    """
    Logout from application and compare state to ensure security

    ProConnect seems to interfere with our session (Starlette session are cookies-based ?) so storing state in session is not an option
    Instead, this quick in-memory cache is used to validate the state parameter.
    """

    state = request.query_params.get("state")
    initial_state = request.session.get("state")

    if not state or not initial_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing state parameter",
        )

    if not state == initial_state:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Possible CSRF attack: state does not match",
        )

    request.session.clear()

    return RedirectResponse("/admin", status_code=302)
