from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/admin/service_providers",
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def service_providers(request: Request):
    """
    Create a new service provider
    """
    return templates.TemplateResponse(
        "service-accounts.html",
        {
            "request": request,
            "user_email": request.session.get("user_email", None),
        },
    )
