from fastapi import APIRouter
from fastapi.security import HTTPBasic

from routers.auth import api, web

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)

# API OAuth2
router.include_router(api.router, include_in_schema=True)

# Web / proconnect based Auth
router.include_router(web.router, include_in_schema=False)


security = HTTPBasic(auto_error=False)
