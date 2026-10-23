"""
Conector para InfoDengue API.
API de dados epidemiológicos de dengue, zika e chikungunya.
"""
import httpx
from datetime import datetime, timedelta
from typing import Optional
from app.ingestion.base import BaseConnector
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class InfoDengueConnector(BaseConnector):
    """Conector para API InfoDengue (info.dengue.mat.br)."""

    def __init__(self):
        super().__init__("infodengue")
        self.base_url = "https://info.dengue.mat.br/api"
        # Código IBGE de Recife
        self.geocode = "2611606"
        # Doenças disponíveis: dengue, chikungunya, zika
        self.diseases = ["dengue", "chikungunya", "zika"]

    async def fetch(self, weeks_back: int = 52) -> dict:
        """
        Busca dados epidemiológicos da API InfoDengue.

        Args:
            weeks_back: Quantas semanas epidemiológicas para trás buscar (padrão: 52 = 1 ano)

        Returns:
            Dict com dados de todas as doenças monitoradas
        """
        # Calcular período (semanas epidemiológicas)
        # IMPORTANTE: Usando 2024 porque estamos em outubro/2024
        # InfoDengue pode ter delay de atualização
        end_date = datetime(2024, 10, 20)  # Data fixa para garantir dados disponíveis
        start_date = end_date - timedelta(weeks=weeks_back)

        # Formato: YYYYWW (ano + semana epidemiológica)
        # InfoDengue usa semanas epidemiológicas (padrão CDC/OMS)
        start_epiweek = f"{start_date.year}{start_date.isocalendar()[1]:02d}"
        end_epiweek = f"{end_date.year}{end_date.isocalendar()[1]:02d}"

        self.logger.info(
            f"Fetching InfoDengue data for Recife",
            extra={
                "geocode": self.geocode,
                "diseases": self.diseases,
                "period": f"{start_epiweek} to {end_epiweek}",
            },
        )

        results = {}
        endpoint_used = None

        async with httpx.AsyncClient(timeout=30.0) as client:
            for disease in self.diseases:
                try:
                    # Endpoint: /alertcity?geocode=XXX&disease=YYY&format=json&ew_start=YYYYWW&ew_end=YYYYWW
                    endpoint = f"{self.base_url}/alertcity"
                    endpoint_used = endpoint

                    params = {
                        "geocode": self.geocode,
                        "disease": disease,
                        "format": "json",
                        "ew_start": start_epiweek,
                        "ew_end": end_epiweek,
                    }

                    response = await client.get(endpoint, params=params)
                    response.raise_for_status()

                    data = response.json()
                    results[disease] = data

                    self.logger.info(
                        f"InfoDengue data fetched for {disease}",
                        extra={
                            "disease": disease,
                            "records": len(data) if isinstance(data, list) else 1,
                            "status_code": response.status_code,
                        },
                    )

                except httpx.HTTPError as e:
                    self.logger.error(
                        f"Failed to fetch {disease} data from InfoDengue",
                        extra={"disease": disease, "error": str(e)},
                    )
                    results[disease] = {"error": str(e)}

        return {
            "endpoint": endpoint_used,
            "params": {
                "geocode": self.geocode,
                "diseases": self.diseases,
                "period": {"start": start_epiweek, "end": end_epiweek},
                "weeks_back": weeks_back,
            },
            "data": results,
            "http_status": 200,
        }

    def get_reference_period(self, payload: dict) -> tuple[datetime, datetime]:
        """Extrai período de referência dos dados."""
        params = payload.get("params", {})
        period = params.get("period", {})

        if not period:
            raise ValueError("No period data in payload")

        # Converter semanas epidemiológicas para datetime
        # Formato YYYYWW -> primeiro dia da semana
        start_epiweek = str(period.get("start", ""))
        end_epiweek = str(period.get("end", ""))

        if len(start_epiweek) >= 6:
            year = int(start_epiweek[:4])
            week = int(start_epiweek[4:6])
            # ISO week date: ano, semana, dia da semana (1=segunda)
            start = datetime.strptime(f"{year}-W{week:02d}-1", "%Y-W%W-%w")
        else:
            start = datetime.now() - timedelta(weeks=52)

        if len(end_epiweek) >= 6:
            year = int(end_epiweek[:4])
            week = int(end_epiweek[4:6])
            end = datetime.strptime(f"{year}-W{week:02d}-1", "%Y-W%W-%w")
        else:
            end = datetime.now()

        return start, end

    def get_transformer(self):
        """Retorna transformador específico para dados epidemiológicos."""
        from app.transformation.infodengue_transformer import InfoDengueTransformer

        return InfoDengueTransformer()
