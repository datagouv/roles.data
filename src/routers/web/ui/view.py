from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import UUID4, EmailStr

from templates.template_manager import ui_template_manager

from ....dependencies import get_activation_service
from ....services.ui.activation_service import ActivationService

router = APIRouter(
    prefix="/ui",
    responses={404: {"description": "Not found"}},
)


@router.get("/activation/succes", response_class=HTMLResponse)
async def home_page(
    request: Request,
    activation_service: ActivationService = Depends(get_activation_service),
):
    user_email: EmailStr | None = request.session.get("user_email", None)
    user_sub: UUID4 | None = request.session.get("user_sub", None)

    if not user_email or not user_sub:
        raise ValueError("User email or sub not found in session.")

    user = await activation_service.activate_user(user_email, user_sub)

    services = await activation_service.get_user_providers(user_email)

    return ui_template_manager.render(
        request,
        "actif.html",
        "Activation de votre compte",
        context={
            "user": user,
            "services": [
                {"name": service.name, "url": service.url} for service in services
            ],
        },
    )


@router.get("/activation", response_class=HTMLResponse)
async def activation_page(request: Request):
    if request.session.get("user_sub", None) is not None:
        return RedirectResponse(url="/ui/activation/succes", status_code=302)

    return ui_template_manager.render(
        request,
        "activation.html",
        "Activation de votre compte",
    )
