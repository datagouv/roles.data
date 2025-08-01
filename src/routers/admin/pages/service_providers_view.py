from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import HttpUrl, ValidationError

from templates.template_manager import Breadcrumb, template_manager

from ....dependencies import get_admin_read_service, get_admin_write_service
from ....services.admin_write_service import AdminWriteService

router = APIRouter(
    prefix="/service-providers",
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_class=HTMLResponse)
async def all_service_providers(
    request: Request, admin_service=Depends(get_admin_read_service)
):
    """
    Allow admin to see the list of service providers
    """
    service_providers = await admin_service.get_service_providers()
    return template_manager.render(
        request,
        "service_providers.html",
        "Liste des fournisseurs de service",
        enforce_authentication=True,
        context={"service_providers": service_providers},
    )


@router.get("/create", response_class=HTMLResponse)
async def create_service_provider_form(request: Request):
    """
    Create a new service provider form
    """
    return template_manager.render(
        request,
        "service_create_form.html",
        "Nouveau FS",
        enforce_authentication=True,
        context={
            "target": "/admin/service-providers/create",
            "fields": [
                {
                    "label": "Nom du FS",
                    "label_hint": "Nom qui sera affiché dans l'interface d'administration",
                    "placeholder": "ex: Data.gouv",
                    "name": "name",
                },
                {
                    "label": "URL du FS",
                    "label_hint": "URL du fournisseur de service",
                    "placeholder": "ex: https://data.gouv.fr",
                    "name": "url",
                },
            ],
        },
        breadcrumbs=[
            Breadcrumb(
                path="/admin/service-providers",
                label="Liste des fournisseurs de service",
            )
        ],
    )


@router.post("/create")
async def create_service_provider(
    request: Request,
    admin_service: AdminWriteService = Depends(get_admin_write_service),
):
    """
    Allow admin to see the list of service providers
    """
    form = await request.form()
    name = str(form.get("name", ""))

    url = ""

    try:
        url = HttpUrl(str(form.get("url", "")))
    except ValidationError:
        raise HTTPException(
            status_code=400,
            detail="Invalid URL format. Please provide a valid URL.",
        )

    service_provider = await admin_service.create_service_provider(
        name=name, url=str(url)
    )

    return RedirectResponse(
        url=f"/admin/service-providers/{service_provider.id}", status_code=303
    )


@router.get("/{service_provider_id}", response_class=HTMLResponse)
async def service_provider(
    request: Request,
    service_provider_id: int,
    admin_service=Depends(get_admin_read_service),
):
    """
    Allow admin to see the detail of a specific service provider
    """
    service_provider = await admin_service.get_service_provider_details(
        service_provider_id
    )
    return template_manager.render(
        request,
        "service_provider.html",
        f"FS n° {service_provider_id}",
        enforce_authentication=True,
        context=service_provider,
        breadcrumbs=[
            Breadcrumb(
                path="/admin/service-providers",
                label="Liste des fournisseurs de service",
            )
        ],
    )


@router.get(
    "/{service_provider_id}/accounts/{account_id}/reset",
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


@router.get("/{service_provider_id}/account/create", response_class=HTMLResponse)
async def create_service_account_form(
    request: Request,
    service_provider_id: int,
):
    """
    Create a new service provider form
    """
    target = f"/admin/service-providers/{service_provider_id}/account/create"
    return template_manager.render(
        request,
        "service_create_form.html",
        "Nouveau compte de service",
        enforce_authentication=True,
        context={
            "target": target,
            "fields": [
                {
                    "label": "client_id du compte de service",
                    "label_hint": "Identifiant unique du compte de service, utilisé pour l'authentification. Pour obtenir le secret, vous devez réinitialiser le compte de service.",
                    "placeholder": "ex: data-gouv-service-account",
                    "name": "name",
                }
            ],
        },
        breadcrumbs=[
            Breadcrumb(
                path="/admin/service-providers",
                label="Liste des fournisseurs de service",
            ),
            Breadcrumb(
                path=f"/admin/service-providers/{service_provider_id}",
                label=f"FS n°{service_provider_id}",
            ),
        ],
    )


@router.post("/{service_provider_id}/account/create")
async def create_service_account(
    request: Request,
    service_provider_id: int,
    admin_service: AdminWriteService = Depends(get_admin_write_service),
):
    """
    Allow admin to see the list of service providers
    """
    if not isinstance(service_provider_id, int) or service_provider_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid service_provider_id. It must be a positive integer.",
        )

    form = await request.form()
    client_id = str(form.get("name", ""))

    await admin_service.create_service_account(
        service_provider_id=service_provider_id, client_id=client_id
    )

    return RedirectResponse(
        url=f"/admin/service-providers/{service_provider_id}", status_code=303
    )


@router.post("/{service_provider_id}/accounts/{account_id}/activate/{state}")
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
