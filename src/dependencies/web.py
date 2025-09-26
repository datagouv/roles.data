from databases import Database
from fastapi import Depends, HTTPException, Request
from pydantic import EmailStr

from ..database import get_db
from ..repositories.admin.admin_read_repository import AdminReadRepository
from ..repositories.admin.admin_write_repository import AdminWriteRepository
from ..repositories.service_providers import ServiceProvidersRepository
from ..repositories.users import UsersRepository
from ..services.admin.read_service import AdminReadService
from ..services.admin.write_service import AdminWriteService
from ..services.logs import LogsService
from ..services.ui.activation_service import ActivationService
from .context import get_logs_service

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


# ==============
# Admin services
# ==============


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


# ===========
# UI services
# ===========


async def get_activation_service(
    db: Database = Depends(get_db),
    logs_service: LogsService = Depends(get_logs_service),
):
    """
    Dependency function that provides an ActivationService instance.
    """
    users_repository = UsersRepository(db, logs_service)
    service_providers_repository = ServiceProvidersRepository(db)
    return ActivationService(users_repository, service_providers_repository)
