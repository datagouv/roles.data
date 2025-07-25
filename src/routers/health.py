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
async def ping(db: Database = Depends(get_db)):
    """
    Vérifie l’état de la connexion à la base de données.
    """
    try:
        async with db.transaction():
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

    except Exception:
        # Log the exception here if needed
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "timestamp": datetime.now().isoformat(),
        }
