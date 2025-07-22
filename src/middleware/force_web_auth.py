from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware


class ForceWebAuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check if the user is authenticated for admin routes and redirect him otherwise
    """

    async def dispatch(self, request: Request, call_next):
        # Only check admin routes
        path = request.url.path

        if path.startswith("/admin/") and not path.startswith("/admin/login"):
            is_super_admin = request.session.get("is_super_admin", False)

            if not is_super_admin:
                return RedirectResponse(url="/admin/login", status_code=302)

            response = await call_next(request)
            return response

        if path.startswith("/ui") and not path.startswith("/ui/activation"):
            user_email = request.session.get("user_email", None)

            if not user_email:
                return RedirectResponse(url="/ui/activation", status_code=302)

            response = await call_next(request)
            return response

        response = await call_next(request)
        return response
