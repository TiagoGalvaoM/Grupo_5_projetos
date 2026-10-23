"""
Conexão com PostgreSQL (Neon) - camada CURATED.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from typing import AsyncGenerator
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Base para modelos SQLAlchemy
Base = declarative_base()

# Engine assíncrono
engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.app_env == "development",
    future=True,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency para FastAPI - fornece sessão do banco."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Inicializa conexão com banco de dados."""
    try:
        async with engine.begin() as conn:
            # Testa conexão
            await conn.execute(text("SELECT 1"))
        logger.info("PostgreSQL (Neon) connected successfully")
    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        raise


async def close_db():
    """Fecha conexão com banco de dados."""
    await engine.dispose()
    logger.info("PostgreSQL disconnected")
