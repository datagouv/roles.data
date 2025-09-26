import logging

import sentry_sdk
from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .database import shutdown, startup
from .documentation import api_description, api_summary, api_tags_metadata
from .middleware.force_web_auth import ForceWebAuthenticationMiddleware
from .routers import (
    groups,
    groups_admin,
    groups_scopes,
    health,
    roles,
    users,
)
from .routers.auth import auth
from .routers.web.admin import view as admin_home
from .routers.web.ui import view as ui_home
from .routers.webhooks import datapass

app = FastAPI(redirect_slashes=True, redoc_url="/")

# =================
# ERROR and logging
# =================

# Configure only application loggers, not FastAPI's built-in ones
app_logger = logging.getLogger("src")  # Your application namespace
app_logger.setLevel(logging.INFO)

if settings.SENTRY_DSN != "":
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=0.1,
        # Capture more information
        attach_stacktrace=True,
        send_default_pii=False,  # Set to True if you want user data
        # Environment information
        environment=settings.DB_ENV,
        # Capture specific integrations
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR,  # Send errors as events
            ),
        ],
        # Sample rate for error events (1.0 = 100%)
        sample_rate=1.0,
        # Enable profiling (optional)
        # profiles_sample_rate=0.1,
        # Before send hook to filter/modify events
        # before_send=lambda event, hint: event if settings.DB_ENV != "test" else None,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if not isinstance(exc, HTTPException):
        sentry_sdk.capture_exception(exc)
        app_logger.error(f"Unexpected exception caught: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )


# =========
# APP SETUP
# =========

# Add template and static files support for HTML/Jinja templating
app.mount("/static", StaticFiles(directory="static"), name="static")


# Register startup and shutdown events (essentially DB connexion)
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)

# health/monitoring
app.include_router(health.router)

# authentication - both web(ProConnect) and API(OAuth2)
app.include_router(auth.router)

# API routers - only use OAuth2
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(groups.router)
app.include_router(groups_admin.router)
app.include_router(groups_scopes.router)

# webhooks (Datapass)
app.include_router(datapass.router)

# web interfaces - only use ProConnect
app.include_router(admin_home.router, include_in_schema=False)
app.include_router(ui_home.router, include_in_schema=False)

# ===========
# Middlewares
# ===========

# In FastAPI/Starlette, middleware is processed in reverse order of how it's added,
# so the last middleware added is executed first.

# force authentication on web paths
# NB : API router authentication is enforced through dependencies
app.add_middleware(ForceWebAuthenticationMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    max_age=3600,
    same_site="lax",
    https_only=settings.IS_PRODUCTION,
    session_cookie="session",  # Consistent cookie name
)


@app.middleware("http")
async def sentry_context_middleware(request: Request, call_next):
    scope = sentry_sdk.get_current_scope()
    scope.set_tag("endpoint", request.url.path)
    scope.set_tag("method", request.method)
    scope.set_context(
        "request",
        {
            "url": str(request.url),
            "method": request.method,
            "headers": dict(request.headers),
        },
    )

    response = await call_next(request)
    return response


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API Rôles.data.gouv.fr",
        version="0.0.1",
        summary=api_summary,
        description=api_description,
        routes=app.routes,
        tags=api_tags_metadata,
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
