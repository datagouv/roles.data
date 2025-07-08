from typing import Any

from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


class TemplateManager:
    def __init__(self, template_dirs: list[str]):
        self.templates = Jinja2Templates(directory=template_dirs)

    def render(
        self,
        request: Request,
        template_name: str,
        enforce_authentication: bool = True,
        context: dict[str, Any] | None = None,
    ):
        """Render template with automatic context enhancement"""
        if context is None:
            context = {}

        user_email = request.session.get("user_email", None)
        is_authenticated = bool(user_email)

        if enforce_authentication and not is_authenticated:
            return RedirectResponse(url="/admin", status_code=303)

        # Add common context
        context.update(
            {
                "request": request,
                "user_email": user_email,
                "is_authenticated": is_authenticated,
            }
        )

        return self.templates.TemplateResponse(template_name, context)


template_manager = TemplateManager(
    [
        "templates",
        "templates/pages",
        "templates/components",
    ]
)
