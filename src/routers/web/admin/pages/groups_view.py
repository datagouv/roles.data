from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from templates.template_manager import Breadcrumb, template_manager

from .....dependencies import get_admin_read_service, get_admin_write_service

router = APIRouter(
    prefix="/groups",
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_class=HTMLResponse)
async def groups_explorer(
    request: Request, admin_service=Depends(get_admin_read_service)
):
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
    request: Request, group_id: int, admin_service=Depends(get_admin_read_service)
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


@router.get("/{group_id}/set-admin/{user_id}", response_class=HTMLResponse)
async def set_admin(
    group_id: int, user_id: int, admin_service=Depends(get_admin_write_service)
):
    """
    Allow admin to name a user admin of a specific group
    """
    if not isinstance(group_id, int) or group_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid group ID. It must be a positive integer.",
        )

    await admin_service.set_admin(group_id, user_id)

    return RedirectResponse(url=f"/admin/groups/{group_id}", status_code=303)
