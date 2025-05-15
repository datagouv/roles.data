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
async def ping(db: Database = Depends(get_db)):
    """
    Health check endpoint to verify if the database is connected and the application is alive.
    """
    try:
        print("hey")
        query = "SELECT schema_name FROM information_schema.schemata;"
        result = await db.fetch_all(query)
        print([dict(r) for r in result])
        print("ho")

        query = "SELECT R.is_admin as is_alive from roles as R WHERE R.role_name = 'administrateur'"
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
        print(e)
        # Log the exception here if needed
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "timestamp": datetime.now().isoformat(),
        }
