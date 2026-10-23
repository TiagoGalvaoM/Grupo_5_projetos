"""
Configuração da aplicação usando Pydantic Settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente."""

    # Application
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    # MongoDB Atlas (RAW layer)
    mongodb_uri: str
    mongodb_database: str = "nexoclima_raw"

    # Neon PostgreSQL (CURATED layer)
    database_url: str

    # External APIs
    open_meteo_base_url: str = "https://api.open-meteo.com"
    recife_latitude: float = -8.05
    recife_longitude: float = -34.9

    # Scheduler
    collection_interval_minutes: int = 60

    # Future AI integration
    llm_provider: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_model: Optional[str] = None

    # Pipeline
    pipeline_version: str = "0.1.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()
