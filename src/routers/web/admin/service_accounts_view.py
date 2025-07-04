from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/admin/service-accounts",
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="templates")


# Add HTML routes alongside your existing API routes
@router.get("/", response_class=HTMLResponse)
async def service_accounts(request: Request):
    """
    Create or update existing service accounts
    """
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user_email": request.session.get("user_email", None),
        },
    )
