"""
Modelos SQLAlchemy para camada CURATED (PostgreSQL/Neon).
"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    Text,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.postgres import Base
import uuid


class DataSource(Base):
    """Cadastro de fontes de dados externas."""

    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    provider = Column(String(255))
    source_type = Column(String(50))  # 'api', 'ckan', 'csv', 'manual'
    url = Column(Text)
    update_frequency = Column(String(50))  # 'hourly', 'daily', 'weekly'
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    measurements = relationship("Measurement", back_populates="source")
    pipeline_runs = relationship("PipelineRun", back_populates="source")


class Indicator(Base):
    """Catálogo de indicadores/variáveis medidas."""

    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True)
    code = Column(String(100), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))  # 'meteorology', 'health', 'environmental'
    unit = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    measurements = relationship("Measurement", back_populates="indicator")


class Territory(Base):
    """Cadastro de territórios (cidade, bairros, regionais)."""

    __tablename__ = "territories"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50))  # 'city', 'neighborhood', 'regional', 'state'
    parent_id = Column(Integer, ForeignKey("territories.id"), nullable=True)
    latitude = Column(Float)
    longitude = Column(Float)
    # geometry para PostGIS será adicionado futuramente
    metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    measurements = relationship("Measurement", back_populates="territory")
    parent = relationship("Territory", remote_side=[id], backref="children")


class Measurement(Base):
    """Medições transformadas (núcleo do sistema)."""

    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    indicator_id = Column(Integer, ForeignKey("indicators.id"), nullable=False)
    territory_id = Column(Integer, ForeignKey("territories.id"), nullable=True)
    reference_time = Column(DateTime(timezone=True), nullable=False)
    collected_at = Column(DateTime(timezone=True), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    raw_ingestion_id = Column(String(24))  # ObjectId do MongoDB
    metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source = relationship("DataSource", back_populates="measurements")
    indicator = relationship("Indicator", back_populates="measurements")
    territory = relationship("Territory", back_populates="measurements")
    classifications = relationship("Classification", back_populates="measurement")

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "indicator_id",
            "territory_id",
            "reference_time",
            name="uq_measurement_key",
        ),
        Index("idx_measurements_reference_time", "reference_time"),
        Index("idx_measurements_source", "source_id"),
        Index("idx_measurements_indicator", "indicator_id"),
        Index("idx_measurements_territory", "territory_id"),
        Index("idx_measurements_collected_at", "collected_at"),
    )


class PipelineRun(Base):
    """Log de execuções do pipeline."""

    __tablename__ = "pipeline_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    finished_at = Column(DateTime(timezone=True))
    status = Column(String(20), nullable=False)  # 'running', 'success', 'error'
    raw_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    error_records = Column(Integer, default=0)
    error_message = Column(Text)
    duration_seconds = Column(Float)
    pipeline_version = Column(String(20))
    metadata = Column(JSONB)

    # Relationships
    source = relationship("DataSource", back_populates="pipeline_runs")

    # Indexes
    __table_args__ = (
        Index("idx_pipeline_runs_source", "source_id", "started_at"),
        Index("idx_pipeline_runs_status", "status", "started_at"),
    )


class Classification(Base):
    """Classificações de medições (Fase 2)."""

    __tablename__ = "classifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    measurement_id = Column(Integer, ForeignKey("measurements.id"), nullable=False)
    classification_type = Column(String(100), nullable=False)
    label = Column(String(100), nullable=False)
    score = Column(Float)
    rule_version = Column(String(20))
    classified_at = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSONB)

    # Relationships
    measurement = relationship("Measurement", back_populates="classifications")

    # Indexes
    __table_args__ = (
        Index("idx_classifications_measurement", "measurement_id"),
        Index("idx_classifications_label", "label", "classified_at"),
    )
