from uuid import UUID

from databases import Database
from fastapi import Depends, HTTPException, Request
from pydantic import EmailStr

from src.auth.o_auth import decode_access_token

from .database import get_db
from .repositories.admin.admin_read_repository import AdminReadRepository
from .repositories.admin.admin_write_repository import AdminWriteRepository
from .repositories.email import EmailRepository
from .repositories.groups import GroupsRepository
from .repositories.logs import LogsRepository
from .repositories.organisations import OrganisationsRepository
from .repositories.roles import RolesRepository
from .repositories.scopes import ScopesRepository
from .repositories.service_account import ServiceAccountRepository
from .repositories.service_providers import ServiceProvidersRepository
from .repositories.users import UsersRepository
from .services.admin.read_service import AdminReadService
from .services.admin.write_service import AdminWriteService
from .services.auth import AuthService
from .services.groups import GroupsService
from .services.logs import LogsService
from .services.organisations import OrganisationsService
from .services.roles import RolesService
from .services.scopes import ScopesService
from .services.services_provider import ServiceProvidersService
from .services.ui.activation_service import ActivationService
from .services.ui.email import EmailService
from .services.users import UsersService

# =================
# Mail dependencies
# =================


async def get_email_service() -> EmailService:
    """
    Dependency function that provides an EmailService instance.
    """
    email_repository = EmailRepository()
    return EmailService(email_repository)


# =========================
# Access Token dependencies
# =========================


def get_logs_service(request: Request) -> LogsService:
    """Dependency to get LogsService instance."""

    try:
        access_token = decode_access_token()
        service_account_id = access_token.get("service_account_id")
        service_provider_id = access_token.get("service_provider_id")

        acting_user_sub = request.query_params.get("acting_user_sub")

        if acting_user_sub is not None:
            try:
                # Cast string to UUID4
                acting_user_sub = UUID(acting_user_sub)
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid UUID format for acting_user_sub: {acting_user_sub}",
                )

        logs_repository = LogsRepository(
            service_provider_id, service_account_id, acting_user_sub
        )
        return LogsService(logs_repository)
    except Exception:
        connected_user_sub = request.session.get("user_sub", None)

        if not connected_user_sub:
            raise HTTPException(
                status_code=403,
                detail="User is not authenticated",
            )

        logs_repository = LogsRepository(
            service_provider_id=0,
            service_account_id=0,
            acting_user_sub=connected_user_sub,
        )
        return LogsService(logs_repository)


# ============
# API services
# ============


async def get_auth_service(
    db: Database = Depends(get_db),
) -> AuthService:
    """
    Dependency function that provides an AuthService instance.
    """
    service_account_repository = ServiceAccountRepository(db)
    return AuthService(service_account_repository)


async def get_users_service(
    db: Database = Depends(get_db), logs_service=Depends(get_logs_service)
) -> UsersService:
    """
    Dependency function that provides a UsersService instance.
    """
    users_repository = UsersRepository(db, logs_service)
    return UsersService(users_repository)


async def get_organisations_service(
    db: Database = Depends(get_db), logs_service=Depends(get_logs_service)
) -> OrganisationsService:
    """
    Dependency function that provides a OrganisationsService instance.
    """
    organisations_repository = OrganisationsRepository(db, logs_service)
    return OrganisationsService(organisations_repository)


async def get_roles_service(db: Database = Depends(get_db)) -> RolesService:
    """
    Dependency function that provides a RolesService instance.
    """
    roles_repository = RolesRepository(db)
    return RolesService(roles_repository)


async def get_service_providers_service(
    db: Database = Depends(get_db),
) -> ServiceProvidersService:
    """
    Dependency function that provides a Service Providers Service instance.
    """
    service_providers_repository = ServiceProvidersRepository(db)
    return ServiceProvidersService(service_providers_repository)


async def get_scopes_service(
    db: Database = Depends(get_db), logs_service=Depends(get_logs_service)
) -> ScopesService:
    """
    Dependency function that provides a ScopeService instance.
    """
    scopes_repository = ScopesRepository(db, logs_service)
    return ScopesService(scopes_repository)


async def get_groups_service(
    db: Database = Depends(get_db),
    access_token=Depends(decode_access_token),
    users_service: UsersService = Depends(get_users_service),
    roles_service: RolesService = Depends(get_roles_service),
    organisations_service: OrganisationsService = Depends(get_organisations_service),
    service_provider_service: ServiceProvidersService = Depends(
        get_service_providers_service
    ),
    scopes_service: ScopesService = Depends(get_scopes_service),
    email_service: EmailService = Depends(get_email_service),
    logs_service=Depends(get_logs_service),
) -> GroupsService:
    """
    Dependency function that provides a GroupsService instance.
    """
    groups_repository = GroupsRepository(db, logs_service)
    service_provider_id = access_token.get("service_provider_id")

    return GroupsService(
        groups_repository,
        users_service,
        roles_service,
        organisations_service,
        service_provider_service,
        scopes_service,
        email_service,
        service_provider_id,
    )


# =====================
# Web (UI) dependencies
# =====================


async def get_proconnected_user_email(request: Request):
    """
    Dependency function that extracts the ProConnect user email from the request.
    """
    user_email = request.session.get("user_email", None)
    if not user_email:
        raise HTTPException(
            status_code=403,
            detail="User is not authenticated",
        )
    return user_email


async def get_admin_read_service(
    user_email: EmailStr = Depends(get_proconnected_user_email),
    db: Database = Depends(get_db),
):
    """
    Dependency function that provides an AdminReadService instance.
    """
    admin_read_repository = AdminReadRepository(db, admin_email=user_email)
    return AdminReadService(admin_read_repository)


async def get_admin_write_service(
    user_email: EmailStr = Depends(get_proconnected_user_email),
    db: Database = Depends(get_db),
):
    """
    Dependency function that provides an AdminWriteService instance.
    """
    admin_write_repository = AdminWriteRepository(db, admin_email=user_email)
    return AdminWriteService(admin_write_repository)


async def get_activation_service(
    db: Database = Depends(get_db), logs_service=Depends(get_logs_service)
):
    """
    Dependency function that provides an ActivationService instance.
    """
    users_repository = UsersRepository(db, logs_service)
    return ActivationService(users_repository)
