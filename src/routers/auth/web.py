import secrets
from urllib.parse import urlencode

from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from auth.pro_connect import pro_connect_provider
from src.config import settings

# This is a router for ProConnect authentication
# It handles login, callback, and logout functionality
# It uses OAuth2 with OpenID Connect to authenticate users via ProConnect

# It is not the same as the main auth router and is only useful for web interfaces


class CONNEXION_TYPE:
    ADMIN = "admin"
    UI = "ui"


router = APIRouter(
    prefix="/pro-connect",
    responses={404: {"description": "Not found"}},
)


async def pro_connect_authorize_url(request: Request):
    """
    Generate the ProConnect authorization URL.
    This is used for both admin and UI login.
    """
    if not settings.PROCONNECT_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ProConnect authentication is not enabled.",
        )

    redirect_uri = request.url_for("callback")
    authorize_url = await pro_connect_provider.proconnect.authorize_redirect(
        request, redirect_uri, acr_values="eidas1"
    )
    return authorize_url


@router.get("/login/ui")
async def login_ui(request: Request):
    """ProConnect login for UI"""
    request.session["connexion_type"] = CONNEXION_TYPE.UI
    return await pro_connect_authorize_url(request)


@router.get("/login/admin")
async def login_admin(request: Request):
    """ProConnect login for admin"""
    request.session["connexion_type"] = CONNEXION_TYPE.ADMIN
    return await pro_connect_authorize_url(request)


@router.get("/callback")
async def callback(request: Request):
    """Create session and actual login after ProConnect callback"""
    try:
        token = await pro_connect_provider.proconnect.authorize_access_token(request)

        # Store the user info in the session, it'll be used when logging out from ProConnect.
        userinfo = await pro_connect_provider.userinfo(token=token)

        connexion_type = request.session.get("connexion_type", None)
        del request.session["connexion_type"]

        if connexion_type == CONNEXION_TYPE.UI:
            request.session["id_token"] = token["id_token"]
            request.session["user_email"] = userinfo["email"]
            request.session["user_sub"] = userinfo["sub"]
            request.session["is_super_admin"] = False

            return RedirectResponse(
                url="/ui/activation/succes", status_code=status.HTTP_302_FOUND
            )

        if connexion_type == CONNEXION_TYPE.ADMIN:
            if userinfo["email"] not in settings.SUPER_ADMIN_EMAILS:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to access this resource.",
                )

            request.session["id_token"] = token["id_token"]
            request.session["is_super_admin"] = True
            request.session["user_email"] = userinfo["email"]
            request.session["user_sub"] = userinfo["sub"]

            return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)

        if not connexion_type:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Connexion type not set in session.",
            )

    except OAuthError as e:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=f"OAuth error: {str(e)}"
        )


@router.get("/logout")
async def logout(request: Request):
    """Logout from ProConnect"""
    id_token = request.session["id_token"]

    # Redirect to ProConnect logout
    metadata = await pro_connect_provider.proconnect.load_server_metadata()
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
