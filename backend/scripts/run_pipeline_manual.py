"""
Script para executar pipeline manualmente (útil para testes).
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.postgres import AsyncSessionLocal
from app.db.mongodb import mongodb
from app.services.pipeline_service import PipelineService
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


async def main():
    """Executa pipeline Weather manualmente."""
    logger.info("Starting manual pipeline execution...")

    # Conecta MongoDB
    await mongodb.connect()

    try:
        async with AsyncSessionLocal() as db:
            service = PipelineService(
                db_session=db, mongodb_collection=mongodb.get_collection("raw_ingestions")
            )

            result = await service.run_weather_pipeline()

            logger.info(f"Pipeline result: {result}")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise
    finally:
        await mongodb.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
