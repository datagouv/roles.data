from dataclasses import dataclass

from src.config import settings


def _parse_emails(raw_emails: str) -> set[str]:
    return {
        email.strip().lower()
        for email in raw_emails.split(",")
        if email and email.strip()
    }


@dataclass(frozen=True)
class WebAdminPermissions:
    is_admin: bool
    is_super_admin: bool
    is_viewer_admin: bool

    @property
    def can_view_admin_logs(self) -> bool:
        return self.is_admin

    @property
    def can_write_admin(self) -> bool:
        return self.is_super_admin

    @property
    def can_view_admin_service_providers(self) -> bool:
        return self.is_super_admin


def get_web_admin_permissions(email: str | None) -> WebAdminPermissions:
    normalized_email = email.strip().lower() if email else ""
    super_admin_emails = _parse_emails(settings.SUPER_ADMIN_EMAILS)
    viewer_admin_emails = _parse_emails(settings.VIEWER_ADMIN_EMAILS)

    is_super_admin = normalized_email in super_admin_emails
    is_viewer_admin = not is_super_admin and normalized_email in viewer_admin_emails

    return WebAdminPermissions(
        is_admin=is_super_admin or is_viewer_admin,
        is_super_admin=is_super_admin,
        is_viewer_admin=is_viewer_admin,
    )
