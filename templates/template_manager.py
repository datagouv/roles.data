from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict


class Breadcrumb(BaseModel):
    path: str
    label: str

    model_config = ConfigDict(from_attributes=True)


class TemplateManager:
    def __init__(self, template_dirs: list[str], admin_pages: bool = False):
        self.templates = Jinja2Templates(directory=template_dirs)
        self.admin_pages = admin_pages

    def render(
        self,
        request: Request,
        template_name: str,
        title: str,
        context: dict[str, Any] | None = None,
        breadcrumbs: list[Breadcrumb] = [],
    ):
        """Render template with automatic context enhancement"""
        if context is None:
            context = {}

        # Add common context
        context.update(
            {
                "title": title,
                "request": request,
                "user_email": request.session.get("user_email", None),
                "is_super_admin": request.session.get("is_super_admin", False),
                "is_authenticated": bool(request.session.get("user_email", None)),
                "breadcrumb_items": [Breadcrumb(path="/admin", label="Accueil")]
                + breadcrumbs,
            }
        )

        return self.templates.TemplateResponse(template_name, context)


ui_template_manager = TemplateManager(
    [
        "templates",
        "templates/pages/ui",
        "templates/components",
    ]
)

admin_template_manager = TemplateManager(
    [
        "templates",
        "templates/pages/admin",
        "templates/components",
    ]
)
