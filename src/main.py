import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi

from src.routers import groups_admin, groups_scopes

from .config import settings
from .database import shutdown, startup
from .documentation import api_description, api_summary, api_tags_metadata
from .routers import auth, groups, health, roles, service_providers, users

if settings.SENTRY_DSN != "":
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=0.1,
    )

app = FastAPI(redirect_slashes=True, redoc_url="/")


@app.middleware("http")
async def debug_headers(request: Request, call_next):
    print(f"Host: {request.headers.get('host')}")
    print(f"X-Forwarded-Host: {request.headers.get('x-forwarded-host')}")
    print(f"X-Forwarded-Proto: {request.headers.get('x-forwarded-proto')}")
    print(f"URL: {request.url}")

    response = await call_next(request)
    return response


# Register startup and shutdown events
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(service_providers.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(groups.router)
app.include_router(groups_admin.router)
app.include_router(groups_scopes.router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="D-rôles",
        version="0.0.1",
        summary=api_summary,
        description=api_description,
        routes=app.routes,
        tags=api_tags_metadata,
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
