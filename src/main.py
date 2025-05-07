from fastapi import FastAPI

from .database import shutdown, startup
from .routers import auth, groups, health, roles, service_providers, users

app = FastAPI()

# Register startup and shutdown events
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)

app.include_router(health.router)
app.include_router(users.router)
app.include_router(groups.router)
app.include_router(roles.router)
app.include_router(service_providers.router)
app.include_router(auth.router)
