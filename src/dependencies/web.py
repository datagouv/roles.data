from uuid import UUID

from databases import Database
from fastapi import Depends, HTTPException, Request
from pydantic import EmailStr

from src.database import get_db
from src.repositories.groups import GroupsRepository
from src.repositories.logs import LogsRepository
from src.repositories.admin.admin_read_repository import AdminReadRepository
from src.repositories.admin.admin_write_repository import AdminWriteRepository
from src.services.logs import LogsService
from src.services.admin.read_service import AdminReadService
from src.services.admin.write_service import AdminWriteService

# =====================
# Web dependencies
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
    request: Request,
    user_email: EmailStr = Depends(get_proconnected_user_email),
    db: Database = Depends(get_db),
):
    """
    Dependency function that provides an AdminWriteService instance.
    """
    acting_user_sub = None
    user_sub = request.session.get("user_sub", None)
    if user_sub:
        acting_user_sub = UUID(user_sub, version=4)

    admin_write_repository = AdminWriteRepository(db, admin_email=user_email)
    logs_service = LogsService(
        LogsRepository(
            service_provider_id=0,
            service_account_id=0,
            acting_user_sub=acting_user_sub,
        )
    )
    groups_repository = GroupsRepository(db, logs_service)
    return AdminWriteService(admin_write_repository, groups_repository)
