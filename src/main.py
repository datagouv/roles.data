from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from .database import shutdown, startup
from .documentation import api_description, api_summary, api_tags_metadata
from .routers import auth, groups, health, roles, service_providers, users

app = FastAPI(redirect_slashes=True)

# Register startup and shutdown events
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(users.router)
app.include_router(groups.router)
app.include_router(roles.router)
app.include_router(service_providers.router)


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
