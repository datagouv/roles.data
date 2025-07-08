from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from routers.web.admin.pages import groups_view
from src.routers.web.admin.pages import logs_view
from templates.template_manager import template_manager

router = APIRouter(
    prefix="/admin",
    responses={404: {"description": "Not found"}},
)


router.include_router(logs_view.router, include_in_schema=False)
router.include_router(groups_view.router, include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return template_manager.render(
        request,
        "home.html",
        "Connexion",
        enforce_authentication=False,
        context={
            "request": request,
            "user_email": request.session.get("user_email", None),
        },
    )
