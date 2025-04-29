# ------- HEALTH CHECK ROUTER FILE -------
from datetime import datetime

from databases import Database
from fastapi import APIRouter, Depends

from ..database import get_db

router = APIRouter(
    prefix="/health",
    tags=["Health check"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def health_check(db: Database = Depends(get_db)):
    try:
        # Test database connection with a simple query
        query = "SELECT R.is_admin as is_alive from d_roles.roles as R WHERE R.role_name = 'admin'"
        result = await db.fetch_one(query)

        if result and result["is_alive"] == 1:
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise Exception("Database query returned unexpected result")

    except Exception:
        # Log the exception here if needed
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "timestamp": datetime.now().isoformat(),
        }
