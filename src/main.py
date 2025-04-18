from fastapi import FastAPI

from . import database
from .routers import users

app = FastAPI()

# Register startup and shutdown events
app.add_event_handler("startup", database.startup)
app.add_event_handler("shutdown", database.shutdown)

app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
