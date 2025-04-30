from fastapi import FastAPI

from . import database
from .routers import groups, health, roles, service_providers, users

app = FastAPI()

# Register startup and shutdown events
app.add_event_handler("startup", database.startup)
app.add_event_handler("shutdown", database.shutdown)

app.include_router(health.router)
app.include_router(users.router)
app.include_router(groups.router)
app.include_router(roles.router)
app.include_router(service_providers.router)
# app.include_router(auth.router)
