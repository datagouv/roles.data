from uuid import UUID

from databases import Database
from fastapi import Depends, HTTPException, Request

from src.auth import decode_access_token
from src.repositories.admin.admin_repository import AdminRepository
from src.repositories.auth import AuthRepository
from src.repositories.logs import LogsRepository
from src.repositories.scopes import ScopesRepository
from src.repositories.service_providers import ServiceProvidersRepository
from src.services.admin.admin_service import AdminService
from src.services.auth import AuthService
from src.services.logs import LogsService
from src.services.scopes import ScopesService
from src.services.services_provider import ServiceProvidersService

from .database import get_db
from .repositories.groups import GroupsRepository
from .repositories.organisations import OrganisationsRepository
from .repositories.roles import RolesRepository
from .repositories.users import UsersRepository
from .services.groups import GroupsService
from .services.organisations import OrganisationsService
from .services.roles import RolesService
from .services.users import UsersService

# =========================
# Access Token dependencies
# =========================


def get_service_provider_id(access_token: dict = Depends(decode_access_token)):
    """
    Dependency function that extracts the service provider ID from the access token.
    """
    return access_token.get("service_provider_id")


def get_service_account_id(access_token: dict = Depends(decode_access_token)):
    """
    Dependency function that extracts the service account ID from the access token.
    """
    return access_token.get("service_account_id")


def get_logs_service(
    request: Request,
    service_provider_id=Depends(get_service_provider_id),
    service_account_id=Depends(get_service_account_id),
) -> LogsService:
    """Dependency to get LogsService instance."""

    acting_user_sub = request.query_params.get("acting_user_sub")

    if acting_user_sub is not None:
        if acting_user_sub.lower() == "false":
            acting_user_sub = None
        else:
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


# =======================
# DB related dependencies
# =======================


async def get_auth_service(
    db: Database = Depends(get_db),
) -> AuthService:
    """
    Dependency function that provides an AuthService instance.
    """
    auth_repository = AuthRepository(db)
    return AuthService(auth_repository)


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
    users_service: UsersService = Depends(get_users_service),
    roles_service: RolesService = Depends(get_roles_service),
    organisations_service: OrganisationsService = Depends(get_organisations_service),
    service_provider_service: ServiceProvidersService = Depends(
        get_service_providers_service
    ),
    scopes_service: ScopesService = Depends(get_scopes_service),
    service_provider_id=Depends(get_service_provider_id),
    logs_service=Depends(get_logs_service),
) -> GroupsService:
    """
    Dependency function that provides a GroupsService instance.
    """
    groups_repository = GroupsRepository(db, logs_service)

    return GroupsService(
        groups_repository,
        users_service,
        roles_service,
        organisations_service,
        service_provider_service,
        scopes_service,
        service_provider_id,
    )


# ================================
# Admin (web) related dependencies
# ================================


async def get_admin_service(
    db: Database = Depends(get_db),
) -> AdminService:
    """
    Dependency function that provides an AdminService instance.
    """
    admin_repository = AdminRepository(db)
    return AdminService(admin_repository)
