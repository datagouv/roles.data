from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from src.dependencies import get_admin_service
from templates.template_manager import template_manager

router = APIRouter(
    prefix="/logs",
    responses={404: {"description": "Not found"}},
)


# Add HTML routes alongside your existing API routes
@router.get("/", response_class=HTMLResponse)
async def logs_explorer(request: Request, admin_service=Depends(get_admin_service)):
    """
    Allow admin to explore the logs of any groups for any service provider. Debug purpose only
    """
    logs = await admin_service.get_logs()
    return template_manager.render(
        request,
        "logs.html",
        "Explorateur de logs",
        enforce_authentication=True,
        context={"logs": logs},
    )
