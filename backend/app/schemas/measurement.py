"""
Pydantic schemas para Measurements e entidades relacionadas.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DataSourceBase(BaseModel):
    name: str
    provider: Optional[str] = None
    source_type: Optional[str] = None
    url: Optional[str] = None
    update_frequency: Optional[str] = None
    active: bool = True


class DataSourceResponse(DataSourceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class IndicatorBase(BaseModel):
    code: str
    name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    description: Optional[str] = None


class IndicatorResponse(IndicatorBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TerritoryBase(BaseModel):
    code: Optional[str] = None
    name: str
    type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class TerritoryResponse(TerritoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MeasurementBase(BaseModel):
    source_id: int
    indicator_id: int
    territory_id: Optional[int] = None
    reference_time: datetime
    collected_at: datetime
    value: float
    unit: str
    raw_ingestion_id: Optional[str] = None
    metadata: Optional[dict] = None


class MeasurementResponse(MeasurementBase):
    id: int
    created_at: datetime

    # Nested relationships (optional)
    source: Optional[DataSourceResponse] = None
    indicator: Optional[IndicatorResponse] = None
    territory: Optional[TerritoryResponse] = None

    class Config:
        from_attributes = True


class MeasurementWithDetails(BaseModel):
    """Measurement com detalhes de source, indicator, territory."""

    id: int
    value: float
    unit: str
    reference_time: datetime
    collected_at: datetime
    source_name: str
    indicator_code: str
    indicator_name: str
    territory_name: Optional[str] = None
    raw_ingestion_id: Optional[str] = None

    class Config:
        from_attributes = True


class PipelineRunBase(BaseModel):
    source_id: int
    status: str = Field(..., pattern="^(running|success|error)$")
    raw_records: int = 0
    processed_records: int = 0
    error_records: int = 0
    error_message: Optional[str] = None


class PipelineRunResponse(PipelineRunBase):
    id: str  # UUID
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    pipeline_version: Optional[str] = None

    class Config:
        from_attributes = True


class SourceStatusResponse(BaseModel):
    """Status de uma fonte de dados."""

    source_id: int
    source_name: str
    active: bool
    last_run: Optional[datetime] = None
    last_status: Optional[str] = None
    total_measurements: int
