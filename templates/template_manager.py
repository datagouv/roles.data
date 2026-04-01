from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict

from src.utils.admin_permissions import get_web_admin_permissions


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
        permissions = get_web_admin_permissions(request.session.get("user_email", None))
        context.update(
            {
                "title": title,
                "request": request,
                "user_email": request.session.get("user_email", None),
                "is_super_admin": request.session.get("is_super_admin", False),
                "is_viewer_admin": request.session.get(
                    "is_viewer_admin", permissions.is_viewer_admin
                ),
                "is_admin": request.session.get(
                    "is_admin",
                    request.session.get("is_super_admin", False)
                    or permissions.is_admin,
                ),
                "can_view_admin_logs": request.session.get(
                    "can_view_admin_logs",
                    request.session.get("is_admin", False)
                    or permissions.can_view_admin_logs,
                ),
                "can_write_admin": request.session.get(
                    "can_write_admin",
                    request.session.get("is_super_admin", False)
                    or permissions.can_write_admin,
                ),
                "can_view_admin_service_providers": request.session.get(
                    "can_view_admin_service_providers",
                    request.session.get("is_super_admin", False)
                    or permissions.can_view_admin_service_providers,
                ),
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
