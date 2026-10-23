"""Health check endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres import get_db
from app.db.mongodb import get_mongodb
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()


@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db), mongodb: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Health check endpoint - verifica conexões com bancos."""
    try:
        # Testa PostgreSQL
        await db.execute("SELECT 1")

        # Testa MongoDB
        await mongodb.command("ping")

        return {
            "status": "healthy",
            "postgres": "connected",
            "mongodb": "connected",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }
