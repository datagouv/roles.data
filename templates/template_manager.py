from typing import Any

from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict


class Breadcrumb(BaseModel):
    path: str
    label: str

    model_config = ConfigDict(from_attributes=True)


class TemplateManager:
    def __init__(self, template_dirs: list[str]):
        self.templates = Jinja2Templates(directory=template_dirs)

    def render(
        self,
        request: Request,
        template_name: str,
        title: str,
        enforce_authentication: bool = True,
        context: dict[str, Any] | None = None,
        breadcrumbs: list[Breadcrumb] = [],
    ):
        """Render template with automatic context enhancement"""
        if context is None:
            context = {}

        user_email = request.session.get("user_email", None)
        is_authenticated = bool(user_email)

        if enforce_authentication and not is_authenticated:
            return RedirectResponse(url="/admin/login", status_code=303)

        # Add common context
        context.update(
            {
                "title": title,
                "request": request,
                "user_email": user_email,
                "is_authenticated": is_authenticated,
                "breadcrumb_items": [Breadcrumb(path="/admin", label="Accueil")]
                + breadcrumbs,
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
