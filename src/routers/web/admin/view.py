from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from templates.template_manager import admin_template_manager

from .pages import (
    groups_view,
    logs_view,
    service_account_view,
    service_providers_view,
    users_view,
)

router = APIRouter(
    prefix="/admin",
    responses={404: {"description": "Not found"}},
)

router.include_router(logs_view.router, include_in_schema=False)
router.include_router(users_view.router, include_in_schema=False)
router.include_router(groups_view.router, include_in_schema=False)
router.include_router(service_providers_view.router, include_in_schema=False)
router.include_router(service_account_view.router, include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return admin_template_manager.render(
        request,
        "home.html",
        "Accueil",
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return admin_template_manager.render(
        request,
        "connexion.html",
        "Connexion",
    )
