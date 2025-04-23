# ------- HEALTH CHECK ROUTER FILE -------
from datetime import datetime

from databases import Database
from fastapi import APIRouter, Depends

from src.database import get_db

router = APIRouter(
    prefix="/health",
    tags=["Health check"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def health_check(db: Database = Depends(get_db)):
    try:
        # Test database connection with a simple query
        query = "SELECT 1 as is_alive"
        result = await db.fetch_one(query)

        if result and result["is_alive"] == 1:
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise Exception("Database query returned unexpected result")

    except Exception as e:
        # Log the exception here if needed
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }, 503  # Service Unavailable status code
