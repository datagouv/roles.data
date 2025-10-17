from databases import Database
from fastapi import Depends, HTTPException, Request
from pydantic import EmailStr

from ..database import get_db
from ..repositories.admin.admin_read_repository import AdminReadRepository
from ..repositories.admin.admin_write_repository import AdminWriteRepository
from ..services.admin.read_service import AdminReadService
from ..services.admin.write_service import AdminWriteService

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
    user_email: EmailStr = Depends(get_proconnected_user_email),
    db: Database = Depends(get_db),
):
    """
    Dependency function that provides an AdminWriteService instance.
    """
    admin_write_repository = AdminWriteRepository(db, admin_email=user_email)
    return AdminWriteService(admin_write_repository)
