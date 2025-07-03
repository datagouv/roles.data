from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from src.config import Settings

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
        )


oauth = ProConnectOAuth(Settings())


@router.get("/login")
async def login(request: Request):
    """Redirect to ProConnect login"""
    redirect_uri = request.url_for("callback")
    print("============== ProConnect OAuth Login ===============")
    authorize_url = await oauth.proconnect.authorize_redirect(request, redirect_uri)
    print(f"Redirecting to ProConnect: {authorize_url}")
    print(redirect_uri)
    return authorize_url


@router.get("/callback")
async def callback(request: Request):
    """Handle ProConnect callback"""
    try:
        token = await oauth.proconnect.authorize_access_token(request)
        user_info = token.get("userinfo")

        if not user_info:
            # If userinfo not in token, fetch it
            resp = await oauth.proconnect.parse_id_token(token)
            user_info = resp

        # # Process user information
        # user_data = {
        #     "email": user_info.get("email"),
        #     "given_name": user_info.get("given_name"),
        #     "family_name": user_info.get("family_name"),
        #     "sub": user_info.get("sub"),  # ProConnect user ID
        #     "siret": user_info.get("siret"),  # Organization SIRET
        #     "organization_name": user_info.get("organization_name"),
        # }

        # Here you would typically:
        # 1. Check if user exists in your database
        # 2. Create or update user record
        # 3. Generate your own JWT token
        # 4. Set session/cookies

        # For now, redirect to dashboard with user info
        return RedirectResponse(url="/admin", status_code=302)

    except OAuthError as e:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=f"OAuth error: {str(e)}"
        )


@router.get("/logout")
async def logout(request: Request):
    """Logout from ProConnect"""
    # Clear your application session/cookies here

    # Redirect to ProConnect logout

    # logout_url = oauth.proconnect.endSessionUrl()
    # logout_url = f"{os.getenv('PROCONNECT_BASE_URL')}/logout"
    # post_logout_redirect_uri = request.url_for("login_page")

    # logout_params = {"post_logout_redirect_uri": str(post_logout_redirect_uri)}

    # return RedirectResponse(
    #     url=f"{logout_url}?{urlencode(logout_params)}", status_code=302
    # )
