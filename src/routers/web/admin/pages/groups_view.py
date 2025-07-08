from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from src.dependencies import get_admin_service
from templates.template_manager import Breadcrumb, template_manager

router = APIRouter(
    prefix="/groups",
    responses={404: {"description": "Not found"}},
)


# Add HTML routes alongside your existing API routes
@router.get("/", response_class=HTMLResponse)
async def groups_explorer(request: Request, admin_service=Depends(get_admin_service)):
    """
    Allow admin to explore all groups
    """
    groups = await admin_service.get_groups()
    return template_manager.render(
        request,
        "groups.html",
        "Liste des groupes",
        enforce_authentication=True,
        context={"groups": groups},
    )


@router.get("/{group_id}", response_class=HTMLResponse)
async def group_explorer(
    request: Request, group_id: int, admin_service=Depends(get_admin_service)
):
    """
    Allow admin to explore the detail of one specific group
    """
    group = await admin_service.get_group_details(group_id)
    return template_manager.render(
        request,
        "group.html",
        f"Groupe {group_id}",
        enforce_authentication=True,
        context=group,
        breadcrumbs=[Breadcrumb(path="/admin/groups", label="Liste des groupes")],
    )
