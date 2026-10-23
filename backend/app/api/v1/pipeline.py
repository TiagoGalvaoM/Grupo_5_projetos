"""Endpoints para execução e monitoramento do pipeline."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.postgres import get_db
from app.domain.models import PipelineRun, DataSource
from app.schemas.measurement import PipelineRunResponse

router = APIRouter()


@router.get("/pipeline/runs", response_model=list[PipelineRunResponse])
async def list_pipeline_runs(
    source: str = None, limit: int = 50, db: AsyncSession = Depends(get_db)
):
    """Lista execuções do pipeline."""
    query = select(PipelineRun).order_by(desc(PipelineRun.started_at)).limit(limit)

    if source:
        query = query.join(DataSource).where(DataSource.name == source)

    result = await db.execute(query)
    runs = result.scalars().all()

    return [
        {
            "id": str(run.id),
            "source_id": run.source_id,
            "started_at": run.started_at,
            "finished_at": run.finished_at,
            "status": run.status,
            "raw_records": run.raw_records,
            "processed_records": run.processed_records,
            "error_records": run.error_records,
            "error_message": run.error_message,
            "duration_seconds": run.duration_seconds,
            "pipeline_version": run.pipeline_version,
        }
        for run in runs
    ]


@router.post("/pipeline/run/{source_name}")
async def trigger_pipeline_run(source_name: str, db: AsyncSession = Depends(get_db)):
    """
    Dispara execução manual do pipeline para uma fonte.
    (Em produção, pipelines rodam automaticamente via scheduler)
    """
    # Verifica se fonte existe
    result = await db.execute(select(DataSource).where(DataSource.name == source_name))
    source = result.scalar_one_or_none()

    if not source:
        raise HTTPException(status_code=404, detail=f"Fonte '{source_name}' não encontrada")

    if not source.active:
        raise HTTPException(status_code=400, detail=f"Fonte '{source_name}' está inativa")

    # TODO: Implementar execução assíncrona do pipeline
    # Por ora, apenas retorna mensagem indicando que funcionalidade será implementada

    return {
        "message": f"Pipeline para fonte '{source_name}' será executado",
        "source_id": source.id,
        "note": "Execução manual será implementada. Por ora, pipelines rodam automaticamente.",
    }
