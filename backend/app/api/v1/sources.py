"""Endpoints para consulta de fontes de dados."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.postgres import get_db
from app.domain.models import DataSource, PipelineRun, Measurement
from app.schemas.measurement import DataSourceResponse, SourceStatusResponse

router = APIRouter()


@router.get("/sources", response_model=list[DataSourceResponse])
async def list_sources(db: AsyncSession = Depends(get_db)):
    """Lista todas as fontes de dados cadastradas."""
    result = await db.execute(select(DataSource))
    sources = result.scalars().all()
    return sources


@router.get("/sources/status", response_model=list[SourceStatusResponse])
async def get_sources_status(db: AsyncSession = Depends(get_db)):
    """Retorna status de todas as fontes (última execução, total de medições)."""
    # Query complexa com agregações
    from sqlalchemy import text

    sql = """
    SELECT
        ds.id as source_id,
        ds.name as source_name,
        ds.active,
        (
            SELECT MAX(pr.started_at)
            FROM pipeline_runs pr
            WHERE pr.source_id = ds.id
        ) as last_run,
        (
            SELECT pr.status
            FROM pipeline_runs pr
            WHERE pr.source_id = ds.id
            ORDER BY pr.started_at DESC
            LIMIT 1
        ) as last_status,
        COUNT(DISTINCT m.id) as total_measurements
    FROM data_sources ds
    LEFT JOIN measurements m ON ds.id = m.source_id
    GROUP BY ds.id, ds.name, ds.active
    ORDER BY last_run DESC NULLS LAST
    """

    result = await db.execute(text(sql))
    rows = result.fetchall()

    return [
        {
            "source_id": row[0],
            "source_name": row[1],
            "active": row[2],
            "last_run": row[3],
            "last_status": row[4],
            "total_measurements": row[5],
        }
        for row in rows
    ]
