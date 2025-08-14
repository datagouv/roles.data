import sentry_sdk
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
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

if settings.SENTRY_DSN != "":
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=0.1,
    )

app = FastAPI(redirect_slashes=True, redoc_url="/")

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
