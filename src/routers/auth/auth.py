from fastapi import APIRouter
from fastapi.security import HTTPBasic

from src.routers.auth import pro_connect, token

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)

# API OAuth2
router.include_router(token.router, include_in_schema=True)

# Web / proconnect based Auth
router.include_router(pro_connect.router, include_in_schema=False)


security = HTTPBasic(auto_error=False)
