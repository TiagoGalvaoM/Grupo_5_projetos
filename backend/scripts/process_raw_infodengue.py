"""
Script simplificado para processar dados RAW do InfoDengue já no MongoDB.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.mongodb import mongodb
from app.db.postgres import AsyncSessionLocal
from app.core.logging import setup_logging, get_logger
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.domain.models import DataSource, Indicator, Territory, Measurement
from app.transformation.infodengue_transformer import InfoDengueTransformer

setup_logging()
logger = get_logger(__name__)


async def main():
    """Processa documentos RAW do InfoDengue."""
    logger.info("Processing InfoDengue RAW documents...")

    await mongodb.connect()

    async with AsyncSessionLocal() as db:
        try:
            collection = mongodb.get_collection("raw_ingestions")

            # Buscar documentos InfoDengue
            docs = await collection.find({"source": "infodengue"}).to_list(length=100)
            logger.info(f"Found {len(docs)} InfoDengue documents")

            # Buscar source_id
            result = await db.execute(
                select(DataSource).where(DataSource.name == "infodengue")
            )
            source = result.scalar_one_or_none()
            if not source:
                logger.error("InfoDengue source not found")
                return

            # Buscar territory (Recife)
            result = await db.execute(
                select(Territory).where(Territory.name == "Recife")
            )
            territory = result.scalar_one_or_none()
            if not territory:
                logger.error("Recife territory not found")
                return

            # Buscar indicators
            result = await db.execute(select(Indicator))
            indicators = result.scalars().all()
            indicator_ids = {ind.code: ind.id for ind in indicators}

            logger.info(f"Found {len(indicator_ids)} indicators")

            # Processar cada documento
            transformer = InfoDengueTransformer()
            total_measurements = 0

            for doc in docs:
                logger.info(f"Processing document {doc['_id']}")

                measurements = transformer.transform(
                    raw_payload=doc.get("payload", {}),
                    source_id=source.id,
                    indicator_ids=indicator_ids,
                    territory_id=territory.id,
                    raw_ingestion_id=str(doc["_id"]),
                )

                if measurements:
                    # Deduplicar measurements dentro do mesmo batch
                    # (temperatura/umidade podem aparecer múltiplas vezes)
                    seen = set()
                    unique_measurements = []
                    for m in measurements:
                        key = (
                            m["source_id"],
                            m["indicator_id"],
                            m["territory_id"],
                            m["reference_time"],
                        )
                        if key not in seen:
                            seen.add(key)
                            unique_measurements.append(m)

                    logger.info(
                        f"Deduplicated {len(measurements)} -> {len(unique_measurements)} measurements"
                    )

                    # UPSERT measurements
                    stmt = pg_insert(Measurement).values(unique_measurements)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=[
                            "source_id",
                            "indicator_id",
                            "territory_id",
                            "reference_time",
                        ],
                        set_={
                            "collected_at": stmt.excluded.collected_at,
                            "value": stmt.excluded.value,
                            "unit": stmt.excluded.unit,
                            "metadata": stmt.excluded.metadata,
                            "raw_ingestion_id": stmt.excluded.raw_ingestion_id,
                        },
                    )
                    await db.execute(stmt)
                    await db.commit()

                    total_measurements += len(unique_measurements)
                    logger.info(
                        f"Inserted {len(unique_measurements)} measurements from document {doc['_id']}"
                    )

                    # Marcar como processado
                    await collection.update_one(
                        {"_id": doc["_id"]}, {"$set": {"processed": True}}
                    )

            logger.info(f"Processing completed! Total measurements: {total_measurements}")

        except Exception as e:
            logger.error(f"Processing failed: {e}", exc_info=True)
            raise
        finally:
            await mongodb.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
