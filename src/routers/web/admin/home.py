from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.routers.web.admin import (
    logs_view,
    service_accounts_view,
    service_providers_view,
)

router = APIRouter(
    prefix="/admin",
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="templates")

router.include_router(logs_view.router, include_in_schema=False)
router.include_router(service_providers_view.router, include_in_schema=False)
router.include_router(service_accounts_view.router, include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user_email": request.session.get("user_email", None),
        },
    )
