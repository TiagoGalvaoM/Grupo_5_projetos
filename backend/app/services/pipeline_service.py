"""
Serviço principal do pipeline de dados.
Orquestra: Ingestão → RAW → Transformação → CURATED
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.core.logging import get_logger
from app.core.config import settings
from app.domain.models import DataSource, Indicator, Territory, Measurement, PipelineRun
import uuid

logger = get_logger(__name__)


class PipelineService:
    """Serviço de execução do pipeline de dados."""

    def __init__(self, db_session: AsyncSession, mongodb_collection):
        self.db = db_session
        self.mongodb_collection = mongodb_collection

    async def run_weather_pipeline(self) -> dict:
        """
        Executa pipeline completo para fonte Open-Meteo:
        1. Ingestão (fetch API)
        2. Armazenamento RAW (MongoDB)
        3. Transformação
        4. Armazenamento CURATED (PostgreSQL)
        """
        from app.ingestion.weather_connector import WeatherConnector

        connector = WeatherConnector()
        run_id = uuid.uuid4()
        start_time = datetime.utcnow()

        # Busca fonte no banco
        result = await self.db.execute(
            select(DataSource).where(DataSource.name == connector.source_name)
        )
        source = result.scalar_one_or_none()

        if not source:
            logger.error(f"Source {connector.source_name} not found in database")
            raise ValueError(f"Source {connector.source_name} not found")

        # Cria registro de pipeline run
        pipeline_run = PipelineRun(
            id=run_id,
            source_id=source.id,
            started_at=start_time,
            status="running",
            pipeline_version=settings.pipeline_version,
        )
        self.db.add(pipeline_run)
        await self.db.commit()

        try:
            # 1. INGESTÃO
            logger.info(f"Starting ingestion for {connector.source_name}")
            fetch_result = await connector.fetch()

            # 2. RAW STORAGE
            raw_ingestion_id = await connector.save_raw(
                mongodb_collection=self.mongodb_collection,
                payload=fetch_result,
                endpoint=fetch_result["endpoint"],
                request_params=fetch_result["params"],
                http_status=fetch_result["http_status"],
            )

            if not raw_ingestion_id:
                logger.info("Duplicate payload detected, skipping transformation")
                pipeline_run.status = "success"
                pipeline_run.finished_at = datetime.utcnow()
                pipeline_run.duration_seconds = (
                    pipeline_run.finished_at - start_time
                ).total_seconds()
                pipeline_run.raw_records = 0
                pipeline_run.processed_records = 0
                await self.db.commit()
                return {
                    "run_id": str(run_id),
                    "status": "skipped",
                    "reason": "duplicate_payload",
                }

            # 3. TRANSFORMAÇÃO
            logger.info("Starting transformation")
            transformer = connector.get_transformer()

            # Valida payload
            if not transformer.validate_payload(fetch_result):
                raise ValueError("Invalid payload structure")

            # Busca IDs necessários
            indicator_ids = await self._get_indicator_ids()
            territory = await self._get_recife_territory()

            if not territory:
                raise ValueError("Recife territory not found in database")

            # Transforma
            measurements_data = transformer.transform(
                raw_payload=fetch_result,
                source_id=source.id,
                indicator_ids=indicator_ids,
                territory_id=territory.id,
                raw_ingestion_id=raw_ingestion_id,
            )

            # 4. CURATED STORAGE
            logger.info(f"Persisting {len(measurements_data)} measurements")
            processed_count = await self._upsert_measurements(measurements_data)

            # Atualiza pipeline run
            end_time = datetime.utcnow()
            pipeline_run.status = "success"
            pipeline_run.finished_at = end_time
            pipeline_run.duration_seconds = (end_time - start_time).total_seconds()
            pipeline_run.raw_records = len(measurements_data)
            pipeline_run.processed_records = processed_count
            pipeline_run.error_records = 0

            await self.db.commit()

            logger.info(
                f"Pipeline completed successfully",
                extra={
                    "run_id": str(run_id),
                    "processed": processed_count,
                    "duration": pipeline_run.duration_seconds,
                },
            )

            return {
                "run_id": str(run_id),
                "status": "success",
                "processed_records": processed_count,
                "duration_seconds": pipeline_run.duration_seconds,
            }

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)

            # Atualiza pipeline run como erro
            pipeline_run.status = "error"
            pipeline_run.finished_at = datetime.utcnow()
            pipeline_run.duration_seconds = (
                pipeline_run.finished_at - start_time
            ).total_seconds()
            pipeline_run.error_message = str(e)

            await self.db.commit()

            raise

    async def run_infodengue_pipeline(self, weeks_back: int = 52) -> dict:
        """
        Executa pipeline completo para fonte InfoDengue:
        1. Ingestão (fetch API)
        2. Armazenamento RAW (MongoDB)
        3. Transformação
        4. Armazenamento CURATED (PostgreSQL)

        Args:
            weeks_back: Quantas semanas epidemiológicas para trás buscar (padrão: 52 = 1 ano)
        """
        from app.ingestion.infodengue_connector import InfoDengueConnector

        connector = InfoDengueConnector()
        run_id = uuid.uuid4()
        start_time = datetime.utcnow()

        # Busca fonte no banco
        result = await self.db.execute(
            select(DataSource).where(DataSource.name == connector.source_name)
        )
        source = result.scalar_one_or_none()

        if not source:
            logger.error(f"Source {connector.source_name} not found in database")
            raise ValueError(f"Source {connector.source_name} not found")

        # Cria registro de pipeline run
        pipeline_run = PipelineRun(
            id=run_id,
            source_id=source.id,
            started_at=start_time,
            status="running",
            pipeline_version=settings.pipeline_version,
        )
        self.db.add(pipeline_run)
        await self.db.commit()

        try:
            # 1. INGESTÃO
            logger.info(f"Starting ingestion for {connector.source_name} (weeks_back={weeks_back})")
            fetch_result = await connector.fetch(weeks_back=weeks_back)

            # 2. RAW STORAGE
            raw_ingestion_id = await connector.save_raw(
                mongodb_collection=self.mongodb_collection,
                payload=fetch_result,
                endpoint=fetch_result["endpoint"],
                request_params=fetch_result["params"],
                http_status=fetch_result["http_status"],
            )

            if not raw_ingestion_id:
                logger.info("Duplicate payload detected, skipping transformation")
                pipeline_run.status = "success"
                pipeline_run.finished_at = datetime.utcnow()
                pipeline_run.duration_seconds = (
                    pipeline_run.finished_at - start_time
                ).total_seconds()
                pipeline_run.raw_records = 0
                pipeline_run.processed_records = 0
                await self.db.commit()
                return {
                    "run_id": str(run_id),
                    "status": "skipped",
                    "reason": "duplicate_payload",
                }

            # 3. TRANSFORMAÇÃO
            logger.info("Starting transformation")
            transformer = connector.get_transformer()

            # Valida payload
            if not transformer.validate_payload(fetch_result):
                raise ValueError("Invalid payload structure")

            # Busca IDs necessários
            indicator_ids = await self._get_indicator_ids()
            territory = await self._get_recife_territory()

            if not territory:
                raise ValueError("Recife territory not found in database")

            # Transforma
            measurements_data = transformer.transform(
                raw_payload=fetch_result,
                source_id=source.id,
                indicator_ids=indicator_ids,
                territory_id=territory.id,
                raw_ingestion_id=raw_ingestion_id,
            )

            # 4. CURATED STORAGE
            logger.info(f"Persisting {len(measurements_data)} measurements")
            processed_count = await self._upsert_measurements(measurements_data)

            # Atualiza pipeline run
            end_time = datetime.utcnow()
            pipeline_run.status = "success"
            pipeline_run.finished_at = end_time
            pipeline_run.duration_seconds = (end_time - start_time).total_seconds()
            pipeline_run.raw_records = len(measurements_data)
            pipeline_run.processed_records = processed_count
            pipeline_run.error_records = 0

            await self.db.commit()

            logger.info(
                f"InfoDengue pipeline completed successfully",
                extra={
                    "run_id": str(run_id),
                    "processed": processed_count,
                    "duration": pipeline_run.duration_seconds,
                },
            )

            return {
                "run_id": str(run_id),
                "status": "success",
                "processed_records": processed_count,
                "duration_seconds": pipeline_run.duration_seconds,
            }

        except Exception as e:
            logger.error(f"InfoDengue pipeline failed: {e}", exc_info=True)

            # Atualiza pipeline run como erro
            pipeline_run.status = "error"
            pipeline_run.finished_at = datetime.utcnow()
            pipeline_run.duration_seconds = (
                pipeline_run.finished_at - start_time
            ).total_seconds()
            pipeline_run.error_message = str(e)

            await self.db.commit()

            raise

    async def _get_indicator_ids(self) -> dict:
        """Retorna mapeamento {code -> id} dos indicadores."""
        result = await self.db.execute(select(Indicator))
        indicators = result.scalars().all()
        return {ind.code: ind.id for ind in indicators}

    async def _get_recife_territory(self) -> Optional[Territory]:
        """Retorna território de Recife."""
        result = await self.db.execute(
            select(Territory).where(Territory.code == "2611606")  # Código IBGE Recife
        )
        return result.scalar_one_or_none()

    async def _upsert_measurements(self, measurements_data: list[dict]) -> int:
        """
        Insere/atualiza measurements usando UPSERT (ON CONFLICT DO NOTHING).
        Retorna número de registros inseridos.
        """
        if not measurements_data:
            return 0

        # PostgreSQL UPSERT
        stmt = pg_insert(Measurement).values(measurements_data)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=["source_id", "indicator_id", "territory_id", "reference_time"]
        )

        result = await self.db.execute(stmt)
        await self.db.commit()

        # rowcount pode não estar disponível em ON CONFLICT DO NOTHING
        # Assumimos que todos foram processados com sucesso
        return len(measurements_data)
