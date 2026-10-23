"""
Scheduler para execução automática dos pipelines.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.config import settings
from app.core.logging import get_logger
from app.db.postgres import AsyncSessionLocal
from app.db.mongodb import mongodb
from app.services.pipeline_service import PipelineService

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


async def run_weather_pipeline_job():
    """Job agendado para executar pipeline Weather."""
    logger.info("Scheduler: Starting weather pipeline job")

    try:
        async with AsyncSessionLocal() as db:
            service = PipelineService(
                db_session=db, mongodb_collection=mongodb.get_collection("raw_ingestions")
            )
            result = await service.run_weather_pipeline()
            logger.info(f"Scheduler: Weather pipeline completed - {result}")

    except Exception as e:
        logger.error(f"Scheduler: Weather pipeline failed - {e}", exc_info=True)


def start_scheduler():
    """Inicia o scheduler com jobs configurados."""
    logger.info("Starting scheduler...")

    # Job: Weather pipeline
    scheduler.add_job(
        run_weather_pipeline_job,
        trigger=IntervalTrigger(minutes=settings.collection_interval_minutes),
        id="weather_pipeline",
        name="Weather Data Collection Pipeline",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        f"Scheduler started - Weather pipeline will run every {settings.collection_interval_minutes} minutes"
    )


def stop_scheduler():
    """Para o scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
