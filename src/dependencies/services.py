from databases import Database
from fastapi import Depends

from ..database import get_db
from ..repositories.groups import GroupsRepository
from ..repositories.organisations import OrganisationsRepository
from ..repositories.roles import RolesRepository
from ..repositories.scopes import ScopesRepository
from ..repositories.service_account import ServiceAccountRepository
from ..repositories.service_providers import ServiceProvidersRepository
from ..repositories.users import UsersRepository
from ..repositories.users_in_group import UsersInGroupRepository
from ..services.groups import GroupsService
from ..services.logs import LogsService
from ..services.organisations import OrganisationsService
from ..services.roles import RolesService
from ..services.scopes import ScopesService
from ..services.service_accounts import ServiceAccountsService
from ..services.service_providers import ServiceProvidersService
from ..services.ui.email import EmailService
from ..services.users import UsersService
from .context import get_logs_service, get_service_provider_id
from .email import get_email_service

# ============
# API services
# ============


async def get_service_acounts_service(
    db: Database = Depends(get_db),
) -> ServiceAccountsService:
    """
    Dependency function that provides an AuthService instance.
    """
    service_account_repository = ServiceAccountRepository(db)
    return ServiceAccountsService(service_account_repository)


async def get_users_service(
    db: Database = Depends(get_db),
    logs_service: LogsService = Depends(get_logs_service),
) -> UsersService:
    """
    Dependency function that provides a UsersService instance.
    """
    users_repository = UsersRepository(db, logs_service)
    return UsersService(users_repository)


async def get_organisations_service(
    db: Database = Depends(get_db),
    logs_service: LogsService = Depends(get_logs_service),
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
    db: Database = Depends(get_db),
    logs_service: LogsService = Depends(get_logs_service),
) -> ScopesService:
    """
    Dependency function that provides a ScopeService instance.
    """
    scopes_repository = ScopesRepository(db, logs_service)
    return ScopesService(scopes_repository)


async def get_groups_service_factory(
    db: Database = Depends(get_db),
    logs_service: LogsService = Depends(get_logs_service),
    users_service: UsersService = Depends(get_users_service),
    roles_service: RolesService = Depends(get_roles_service),
    organisations_service: OrganisationsService = Depends(get_organisations_service),
    service_provider_service: ServiceProvidersService = Depends(
        get_service_providers_service
    ),
    scopes_service: ScopesService = Depends(get_scopes_service),
    email_service: EmailService = Depends(get_email_service),
):
    """
    Dependency function that returns a factory function to create GroupsService instances for any service provider.

    Returns:
        A function that takes service_provider_id and returns a GroupsService instance
    """
    groups_repository = GroupsRepository(db, logs_service)
    users_in_group_repository = UsersInGroupRepository(db, logs_service)

    def create_groups_service(service_provider_id: int) -> GroupsService:
        return GroupsService(
            groups_repository,
            users_in_group_repository,
            users_service,
            roles_service,
            organisations_service,
            service_provider_service,
            scopes_service,
            email_service,
            service_provider_id,
        )

    return create_groups_service


async def get_groups_service(
    service_provider_id: int = Depends(get_service_provider_id),
    groups_service_factory=Depends(get_groups_service_factory),
) -> GroupsService:
    """
    Dependency function that provides a GroupsService instance using the context's service_provider_id.
    """
    if not service_provider_id:
        raise Exception(
            "Group service should always be used in the context of a Service Provider"
        )

    return groups_service_factory(service_provider_id)
