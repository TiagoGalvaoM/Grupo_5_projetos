"""
Configuração de logging estruturado.
"""
import logging
import sys
from app.core.config import settings


def setup_logging():
    """Configura logging estruturado para a aplicação."""

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Silenciar logs muito verbosos de bibliotecas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Retorna logger configurado para um módulo."""
    return logging.getLogger(name)
