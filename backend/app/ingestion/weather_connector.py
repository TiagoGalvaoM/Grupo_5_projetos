"""
Conector para Open-Meteo Weather API.
"""
import httpx
from datetime import datetime
from typing import Optional
from app.ingestion.base import BaseConnector
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class WeatherConnector(BaseConnector):
    """Conector para API meteorológica Open-Meteo."""

    def __init__(self):
        super().__init__("open_meteo")
        self.base_url = settings.open_meteo_base_url
        self.latitude = settings.recife_latitude
        self.longitude = settings.recife_longitude

    async def fetch(self) -> dict:
        """
        Busca dados meteorológicos da API Open-Meteo.
        """
        endpoint = f"{self.base_url}/v1/forecast"

        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "hourly": ",".join(
                [
                    "temperature_2m",
                    "precipitation",
                    "rain",
                    "precipitation_probability",
                    "relative_humidity_2m",
                    "wind_speed_10m",
                    "weather_code",
                ]
            ),
            "timezone": "America/Recife",
            "forecast_days": 3,  # 3 dias de previsão
        }

        self.logger.info(f"Fetching weather data from Open-Meteo", extra={"params": params})

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()

            data = response.json()
            self.logger.info(
                f"Weather data fetched successfully",
                extra={
                    "status_code": response.status_code,
                    "hours": len(data.get("hourly", {}).get("time", [])),
                },
            )

            return {
                "endpoint": str(response.url),
                "params": params,
                "data": data,
                "http_status": response.status_code,
            }

    def get_reference_period(self, payload: dict) -> tuple[datetime, datetime]:
        """Extrai período de referência dos dados."""
        hourly_data = payload.get("data", {}).get("hourly", {})
        times = hourly_data.get("time", [])

        if not times:
            raise ValueError("No time data in payload")

        # Converter strings ISO para datetime
        start = datetime.fromisoformat(times[0])
        end = datetime.fromisoformat(times[-1])

        return start, end

    def get_transformer(self):
        """Retorna transformador específico para dados meteorológicos."""
        from app.transformation.weather_transformer import WeatherTransformer

        return WeatherTransformer()
