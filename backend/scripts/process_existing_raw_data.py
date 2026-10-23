"""
Script para processar dados RAW existentes no MongoDB que ainda não foram transformados.
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
    """Processa dados RAW não processados."""
    logger.info("Starting processing of existing RAW data...")

    await mongodb.connect()

    async with AsyncSessionLocal() as db:
        try:
            collection = mongodb.get_collection("raw_ingestions")

            # Buscar documentos não processados (processed=False OU processed não existe)
            unprocessed = await collection.find(
                {"$or": [{"processed": False}, {"processed": {"$exists": False}}]}
            ).to_list(length=100)

            logger.info(f"Found {len(unprocessed)} unprocessed documents")

            for doc in unprocessed:
                source = doc.get("source")
                logger.info(
                    f"Processing document {doc['_id']} from source '{source}'"
                )

                # Criar serviço de pipeline
                service = PipelineService(
                    db_session=db,
                    mongodb_collection=collection,
                )

                # Processar dependendo da fonte
                if source == "infodengue":
                    result = await service._transform_and_store_infodengue(
                        raw_doc=doc,
                        source_name="infodengue",
                    )
                    logger.info(f"InfoDengue processing result: {result}")

                elif source == "open-meteo":
                    result = await service._transform_and_store_weather(
                        raw_doc=doc,
                        source_name="open-meteo",
                    )
                    logger.info(f"Weather processing result: {result}")

                else:
                    logger.warning(f"Unknown source: {source}")

            logger.info("Processing completed successfully!")

        except Exception as e:
            logger.error(f"Processing failed: {e}", exc_info=True)
            raise
        finally:
            await mongodb.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
