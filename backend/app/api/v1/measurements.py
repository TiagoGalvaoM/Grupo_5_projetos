"""Endpoints para consulta de medições."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload
from typing import Optional
from datetime import datetime
from app.db.postgres import get_db
from app.domain.models import Measurement, DataSource, Indicator, Territory
from app.schemas.measurement import MeasurementResponse

router = APIRouter()


@router.get("/measurements", response_model=list[MeasurementResponse])
async def get_measurements(
    source: Optional[str] = Query(None, description="Nome da fonte"),
    indicator: Optional[str] = Query(None, description="Código do indicador"),
    start: Optional[datetime] = Query(None, description="Início do período"),
    end: Optional[datetime] = Query(None, description="Fim do período"),
    limit: int = Query(100, le=1000, description="Limite de resultados"),
    db: AsyncSession = Depends(get_db),
):
    """Consulta medições com filtros opcionais."""
    query = (
        select(Measurement)
        .options(
            joinedload(Measurement.source),
            joinedload(Measurement.indicator),
            joinedload(Measurement.territory),
        )
        .order_by(desc(Measurement.reference_time))
    )

    # Aplicar filtros
    if source:
        query = query.join(DataSource).where(DataSource.name == source)

    if indicator:
        query = query.join(Indicator).where(Indicator.code == indicator)

    if start:
        query = query.where(Measurement.reference_time >= start)

    if end:
        query = query.where(Measurement.reference_time <= end)

    query = query.limit(limit)

    result = await db.execute(query)
    measurements = result.unique().scalars().all()

    return measurements


@router.get("/measurements/latest")
async def get_latest_measurements(
    territory_code: Optional[str] = Query(None, description="Código do território"),
    db: AsyncSession = Depends(get_db),
):
    """Retorna as últimas medições por indicador."""
    # Query SQL raw para DISTINCT ON (não suportado diretamente pelo SQLAlchemy ORM)
    from sqlalchemy import text

    sql = """
    SELECT DISTINCT ON (i.code)
        m.id,
        m.value,
        m.unit,
        m.reference_time,
        m.collected_at,
        ds.name as source_name,
        i.code as indicator_code,
        i.name as indicator_name,
        t.name as territory_name
    FROM measurements m
    JOIN data_sources ds ON m.source_id = ds.id
    JOIN indicators i ON m.indicator_id = i.id
    LEFT JOIN territories t ON m.territory_id = t.id
    """

    if territory_code:
        sql += " WHERE t.code = :territory_code"

    sql += " ORDER BY i.code, m.reference_time DESC"

    if territory_code:
        result = await db.execute(text(sql), {"territory_code": territory_code})
    else:
        result = await db.execute(text(sql))

    rows = result.fetchall()

    return [
        {
            "id": row[0],
            "value": row[1],
            "unit": row[2],
            "reference_time": row[3],
            "collected_at": row[4],
            "source_name": row[5],
            "indicator_code": row[6],
            "indicator_name": row[7],
            "territory_name": row[8],
        }
        for row in rows
    ]
