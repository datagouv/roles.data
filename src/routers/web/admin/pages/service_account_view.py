from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from .....dependencies import get_admin_write_service
from .....services.admin.write_service import AdminWriteService

router = APIRouter(
    prefix="/service-providers/{service_provider_id}/accounts",
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/{account_id}/reset",
    response_class=HTMLResponse,
)
async def reset_secret(
    service_provider_id: int,
    account_id: int,
    admin_service=Depends(get_admin_write_service),
):
    """Reset and return the secret"""
    try:
        new_secret = await admin_service.update_service_account(
            service_provider_id, account_id, action="reset_secret"
        )
        return HTMLResponse(f"""
            <div style="background:#eee; padding: 0 10px">
                <code >{new_secret}</code>
            </div>
            """)
    except Exception:
        import logging

        logging.error("Error while resetting the secret", exc_info=True)
        return HTMLResponse("""
        <div class="error-display">
            <span class="fr-badge fr-badge--error fr-badge--sm">
                Une erreur est survenue lors de la réinitialisation du secret.
            </span>
        </div>
        """)


@router.get("/create")
async def create_service_account_form(
    request: Request,
    service_provider_id: int,
    admin_service: AdminWriteService = Depends(get_admin_write_service),
):
    """
    Create a new service provider with random UUID as client_id
    """
    if not isinstance(service_provider_id, int) or service_provider_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid service_provider_id. It must be a positive integer.",
        )

    client_id = str(uuid4())

    await admin_service.create_service_account(
        service_provider_id=service_provider_id, client_id=client_id
    )

    return RedirectResponse(
        url=f"/admin/service-providers/{service_provider_id}", status_code=303
    )


@router.post("/{account_id}/activate/{state}")
async def deactivate_service_account(
    service_provider_id: int,
    account_id: int,
    state: bool,
    admin_service=Depends(get_admin_write_service),
):
    if not isinstance(service_provider_id, int) or service_provider_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid service_provider_id. It must be a positive integer.",
        )

    await admin_service.update_service_account(
        service_provider_id, account_id, action="activate" if state else "deactivate"
    )

    return RedirectResponse(
        url=f"/admin/service-providers/{service_provider_id}", status_code=303
    )
