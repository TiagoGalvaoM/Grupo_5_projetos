"""
Classe base abstrata para conectores de fontes externas.
"""
from abc import ABC, abstractmethod
from typing import Optional, Any
from datetime import datetime
import hashlib
import json
from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseConnector(ABC):
    """Classe base para todos os conectores de fontes externas."""

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.logger = get_logger(f"{__name__}.{source_name}")

    @abstractmethod
    async def fetch(self) -> dict:
        """
        Busca dados da fonte externa.
        Retorna o payload bruto.
        """
        pass

    @abstractmethod
    def get_reference_period(self, payload: dict) -> tuple[datetime, datetime]:
        """
        Extrai período de referência dos dados do payload.
        Retorna (start, end).
        """
        pass

    def generate_payload_hash(self, payload: dict) -> str:
        """Gera hash SHA-256 do payload para deduplicação."""
        payload_json = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(payload_json.encode()).hexdigest()

    async def save_raw(
        self,
        mongodb_collection,
        payload: dict,
        endpoint: str,
        request_params: dict,
        status: str = "success",
        http_status: int = 200,
        error_type: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Optional[str]:
        """
        Salva payload bruto no MongoDB.
        Retorna ObjectId do documento inserido ou None em caso de duplicação.
        """
        from app.core.config import settings

        try:
            reference_start, reference_end = self.get_reference_period(payload)
        except Exception as e:
            self.logger.warning(f"Não foi possível extrair período de referência: {e}")
            reference_start = reference_end = None

        payload_hash = self.generate_payload_hash(payload)

        document = {
            "source": self.source_name,
            "endpoint": endpoint,
            "request_params": request_params,
            "collected_at": datetime.utcnow(),
            "reference_period": (
                {"start": reference_start, "end": reference_end}
                if reference_start and reference_end
                else None
            ),
            "status": status,
            "http_status": http_status,
            "payload": payload if status == "success" else None,
            "payload_hash": payload_hash,
            "pipeline_version": settings.pipeline_version,
            "error_type": error_type,
            "error_message": error_message,
        }

        try:
            result = await mongodb_collection.insert_one(document)
            self.logger.info(
                f"RAW data saved to MongoDB: {result.inserted_id}",
                extra={"source": self.source_name, "status": status},
            )
            return str(result.inserted_id)
        except Exception as e:
            # Duplicação (unique constraint em payload_hash)
            if "duplicate key error" in str(e).lower():
                self.logger.info(
                    f"Duplicate payload detected, skipping insert",
                    extra={"source": self.source_name, "hash": payload_hash[:16]},
                )
                return None
            raise

    @abstractmethod
    def get_transformer(self):
        """
        Retorna o transformador específico para esta fonte.
        """
        pass
