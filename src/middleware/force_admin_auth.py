from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware


class ForceAdminAuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check if the user is authenticated for admin routes and redirect him otherwise
    """

    async def dispatch(self, request: Request, call_next):
        # Only check admin routes
        is_login_page = request.url.path.startswith("/admin/login")

        if not is_login_page and request.url.path.startswith("/admin/"):
            user_email = request.session.get("user_email")

            if not user_email:
                return RedirectResponse(url="/admin/login", status_code=302)

        response = await call_next(request)
        return response
