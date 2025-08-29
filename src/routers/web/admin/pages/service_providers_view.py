from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import HttpUrl, ValidationError

from templates.template_manager import Breadcrumb, admin_template_manager

from .....dependencies import get_admin_read_service, get_admin_write_service
from .....services.admin.write_service import AdminWriteService

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
    return admin_template_manager.render(
        request,
        "service_providers.html",
        "Liste des fournisseurs de service",
        context={"service_providers": service_providers},
    )


@router.get("/create", response_class=HTMLResponse)
async def create_service_provider_form(request: Request):
    """
    Create a new service provider form
    """
    return admin_template_manager.render(
        request,
        "service_create_form.html",
        "Nouveau FS",
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
    service_provider = await admin_service.get_service_accounts_and_logs(
        service_provider_id
    )
    return admin_template_manager.render(
        request,
        "service_provider.html",
        f"FS n° {service_provider_id}",
        context=service_provider,
        breadcrumbs=[
            Breadcrumb(
                path="/admin/service-providers",
                label="Liste des fournisseurs de service",
            )
        ],
    )


@router.get("/{service_provider_id}/update", response_class=HTMLResponse)
async def update_service_provider_form(
    request: Request,
    service_provider_id: int,
    admin_service=Depends(get_admin_read_service),
):
    """
    Update service provider form
    """
    service_provider = await admin_service.get_service_provider_details(
        service_provider_id
    )
    return admin_template_manager.render(
        request,
        "service_create_form.html",
        f"Mettre à jour le FS {service_provider_id}",
        context={
            "target": f"/admin/service-providers/{service_provider_id}/update",
            "fields": [
                {
                    "label": "Nom du FS",
                    "label_hint": "Nom qui sera affiché dans l'interface d'administration",
                    "placeholder": "ex: Data.gouv",
                    "name": "name",
                    "defaultValue": service_provider.name,
                },
                {
                    "label": "URL du FS",
                    "label_hint": "URL du fournisseur de service",
                    "placeholder": "ex: https://data.gouv.fr",
                    "name": "url",
                    "defaultValue": service_provider.url,
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


@router.post("/{service_provider_id}/update")
async def update_service_provider(
    request: Request,
    service_provider_id: int,
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

    await admin_service.update_service_provider(
        service_provider_id=service_provider_id, name=name, url=str(url)
    )

    return RedirectResponse(url="/admin/service-providers", status_code=303)
