from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from pydantic import UUID4, EmailStr

from templates.template_manager import ui_template_manager

from ....dependencies import get_users_service
from ....services.users import UsersService

router = APIRouter(
    prefix="/ui",
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_class=HTMLResponse)
async def home_page(
    request: Request,
    users_service: UsersService = Depends(get_users_service),
):
    user_email: EmailStr | None = request.session.get("user_email", None)
    user_sub: UUID4 | None = request.session.get("user_sub", None)

    if not user_email or not user_sub:
        raise ValueError("User email or sub not found in session.")

    user = await users_service.get_user_by_email(
        email=user_email, only_verified_user=False
    )

    if not user.is_verified:
        await users_service.verify_user(user_sub=user_sub, user_email=user_email)

    return ui_template_manager.render(
        request,
        "accueil.html",
        "Accueil",
        context={
            "user": user,
        },
    )


@router.get("/activation", response_class=HTMLResponse)
async def activation_page(request: Request):
    return ui_template_manager.render(
        request,
        "activation.html",
        "Activation de votre compte",
    )
