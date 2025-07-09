from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from src.dependencies import get_admin_service
from templates.template_manager import Breadcrumb, template_manager

router = APIRouter(
    prefix="/service-providers",
    responses={404: {"description": "Not found"}},
)


# Add HTML routes alongside your existing API routes
@router.get("/", response_class=HTMLResponse)
async def all_service_providers(
    request: Request, admin_service=Depends(get_admin_service)
):
    """
    Allow admin to see the list of service providers
    """
    service_providers = await admin_service.get_service_providers()
    return template_manager.render(
        request,
        "service_providers.html",
        "Liste de fournisseurs de service",
        enforce_authentication=True,
        context={"service_providers": service_providers},
    )


# Add HTML routes alongside your existing API routes
@router.get("/{service_provider_id}", response_class=HTMLResponse)
async def service_provider(
    request: Request, service_provider_id: int, admin_service=Depends(get_admin_service)
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
        f"Fournisseur de service {service_provider_id}",
        enforce_authentication=True,
        context=service_provider,
        breadcrumbs=[
            Breadcrumb(
                path="/admin/service-providers",
                label="Liste de fournisseurs de service",
            )
        ],
    )
