from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from templates.template_manager import template_manager

from .pages import groups_view, logs_view

router = APIRouter(
    prefix="/admin",
    responses={404: {"description": "Not found"}},
)


router.include_router(logs_view.router, include_in_schema=False)
router.include_router(groups_view.router, include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return template_manager.render(
        request,
        "home.html",
        "Accueil",
        enforce_authentication=True,
        context={},
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return template_manager.render(
        request,
        "connexion.html",
        "Connexion",
        enforce_authentication=False,
        context={},
    )
