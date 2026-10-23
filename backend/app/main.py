"""
Aplicação principal FastAPI do NexoClima.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.db.mongodb import mongodb
from app.db.postgres import init_db, close_db
from app.api.v1 import health, measurements, sources, pipeline
from app.services.scheduler import start_scheduler, stop_scheduler

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia startup e shutdown da aplicação."""
    # Startup
    setup_logging()
    logger.info(f"Starting NexoClima API - Environment: {settings.app_env}")

    # Conecta bancos de dados
    await mongodb.connect()
    await init_db()

    # Inicia scheduler (coleta automática)
    if settings.app_env != "test":
        start_scheduler()

    logger.info("NexoClima API started successfully")

    yield

    # Shutdown
    logger.info("Shutting down NexoClima API")
    stop_scheduler()
    await mongodb.disconnect()
    await close_db()


app = FastAPI(
    title="NexoClima API",
    description="API para integração de dados climáticos e saúde - Vigidesastres Recife",
    version=settings.pipeline_version,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar para produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, tags=["Health"])
app.include_router(measurements.router, prefix="/api/v1", tags=["Measurements"])
app.include_router(sources.router, prefix="/api/v1", tags=["Sources"])
app.include_router(pipeline.router, prefix="/api/v1", tags=["Pipeline"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "NexoClima API",
        "version": settings.pipeline_version,
        "description": "Sistema de integração de dados climáticos e saúde",
        "docs": "/docs",
    }
