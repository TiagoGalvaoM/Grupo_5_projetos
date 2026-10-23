"""
Script para executar pipeline InfoDengue manualmente.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.mongodb import mongodb
from app.db.postgres import AsyncSessionLocal
from app.services.pipeline_service import PipelineService
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


async def main():
    """Executa pipeline InfoDengue manualmente."""
    logger.info("Starting manual InfoDengue pipeline execution...")

    # Conecta ao MongoDB
    await mongodb.connect()

    async with AsyncSessionLocal() as db:
        try:
            # Cria serviço de pipeline
            service = PipelineService(
                db_session=db, mongodb_collection=mongodb.get_collection("raw_ingestions")
            )

            # Executa pipeline (últimas 8 semanas para teste)
            result = await service.run_infodengue_pipeline(weeks_back=8)

            logger.info(f"Pipeline result: {result}")

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise
        finally:
            await mongodb.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
