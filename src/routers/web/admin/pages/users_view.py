from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from src.dependencies import get_admin_read_service, get_admin_write_service
from src.services.admin.read_service import AdminReadService
from templates.template_manager import Breadcrumb, admin_template_manager

router = APIRouter(
    prefix="/users",
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_class=HTMLResponse)
async def users_explorer(
    request: Request, admin_service: AdminReadService = Depends(get_admin_read_service)
):
    """
    Allow admin to explore all groups
    """
    users = await admin_service.get_users()
    return admin_template_manager.render(
        request,
        "utilisateurs.html",
        "Liste des utilisateurs",
        context={"users": users},
    )


@router.get("/{user_id}", response_class=HTMLResponse)
async def user_explorer(
    request: Request, user_id: int, admin_service=Depends(get_admin_read_service)
):
    """
    Allow admin to explore the detail of one specific group
    """
    group = await admin_service.get_user_details(user_id)

    return admin_template_manager.render(
        request,
        "utilisateur.html",
        f"Utilisateur {user_id}",
        context=group,
        breadcrumbs=[Breadcrumb(path="/admin/users", label="Liste des utilisateurs")],
    )


@router.delete("/{user_id}", response_class=RedirectResponse)
async def delete_user(user_id: int, admin_service=Depends(get_admin_write_service)):
    """
    Allow super admin to delete a user and all their relationships
    """
    if not isinstance(user_id, int) or user_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid user ID. It must be a positive integer.",
        )

    await admin_service.delete_user(user_id)

    return RedirectResponse(url="/admin/users", status_code=303)
