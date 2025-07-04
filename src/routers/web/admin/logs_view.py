from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/admin/logs",
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="templates")


# Add HTML routes alongside your existing API routes
@router.get("/", response_class=HTMLResponse)
async def logs_explorer(request: Request):
    """
    Allow admin to explore the logs of any groups for any service provider. Debug purpose only
    """
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user_email": request.session.get("user_email", None),
        },
    )
