# Re-export all dependencies for backward compatibility
# This allows existing imports like `from src.dependencies import get_logs_service` to continue working

# Context dependencies
from .context import (
    get_context,
    get_logs_service,
    get_service_account_id,
    get_service_provider_id,
)

# Webhook dependencies
from .datapass import get_verified_datapass_payload

# Email dependencies
from .email import get_email_service

# Service dependencies
from .services import (
    get_groups_service,
    get_groups_service_factory,
    get_organisations_service,
    get_roles_service,
    get_scopes_service,
    get_service_acounts_service,
    get_service_providers_service,
    get_users_service,
)

# Admin dependencies
from .web import (
    get_activation_service,
    get_admin_read_service,
    get_admin_write_service,
    get_proconnected_user_email,
)

# Make all imports available at package level
__all__ = [
    # Context
    "get_context",
    "get_logs_service",
    "get_service_account_id",
    "get_service_provider_id",
    # Email
    "get_email_service",
    # Services
    "get_groups_service",
    "get_groups_service_factory",
    "get_organisations_service",
    "get_roles_service",
    "get_scopes_service",
    "get_service_acounts_service",
    "get_service_providers_service",
    "get_users_service",
    # Admin
    "get_activation_service",
    "get_admin_read_service",
    "get_admin_write_service",
    "get_proconnected_user_email",
    # Webhooks
    "get_verified_datapass_payload",
]
