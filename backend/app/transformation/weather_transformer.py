"""
Transformador de dados meteorológicos (Open-Meteo).
"""
from datetime import datetime
from typing import List, Dict, Any
from app.core.logging import get_logger

logger = get_logger(__name__)


class WeatherTransformer:
    """Transforma dados brutos da API Open-Meteo em modelo interno."""

    # Mapeamento de campos Open-Meteo para indicadores internos
    INDICATOR_MAPPING = {
        "temperature_2m": {"code": "temp_2m", "unit": "celsius"},
        "precipitation": {"code": "precipitation", "unit": "mm"},
        "rain": {"code": "rain", "unit": "mm"},
        "precipitation_probability": {"code": "precip_prob", "unit": "percent"},
        "relative_humidity_2m": {"code": "humidity", "unit": "percent"},
        "wind_speed_10m": {"code": "wind_speed", "unit": "km/h"},
        "weather_code": {"code": "weather_code", "unit": "wmo_code"},
    }

    def transform(
        self,
        raw_payload: dict,
        source_id: int,
        indicator_ids: dict,
        territory_id: int,
        raw_ingestion_id: str,
    ) -> List[dict]:
        """
        Transforma payload bruto em lista de measurements.

        Args:
            raw_payload: Payload bruto do MongoDB
            source_id: ID da fonte no PostgreSQL
            indicator_ids: Mapeamento {code -> id} dos indicadores
            territory_id: ID do território
            raw_ingestion_id: ObjectId do documento RAW

        Returns:
            Lista de dicionários representando measurements
        """
        measurements = []

        data = raw_payload.get("data", {})
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])

        if not times:
            logger.warning("No time data in payload, skipping transformation")
            return measurements

        # Use current UTC time as collection time
        collected_at = datetime.utcnow()

        # Para cada timestamp
        for i, time_str in enumerate(times):
            reference_time = datetime.fromisoformat(time_str)

            # Para cada indicador
            for field_name, mapping in self.INDICATOR_MAPPING.items():
                if field_name not in hourly:
                    continue

                values = hourly[field_name]
                if i >= len(values):
                    continue

                value = values[i]

                # Skip valores nulos
                if value is None:
                    continue

                indicator_code = mapping["code"]
                unit = mapping["unit"]

                # Verifica se indicador existe
                if indicator_code not in indicator_ids:
                    logger.warning(
                        f"Indicator {indicator_code} not found in database, skipping"
                    )
                    continue

                measurement = {
                    "source_id": source_id,
                    "indicator_id": indicator_ids[indicator_code],
                    "territory_id": territory_id,
                    "reference_time": reference_time,
                    "collected_at": collected_at,
                    "value": float(value),
                    "unit": unit,
                    "raw_ingestion_id": raw_ingestion_id,
                    "metadata": {
                        "latitude": data.get("latitude"),
                        "longitude": data.get("longitude"),
                        "timezone": data.get("timezone"),
                    },
                }

                measurements.append(measurement)

        logger.info(
            f"Transformed {len(measurements)} measurements from {len(times)} timestamps"
        )

        return measurements

    @staticmethod
    def validate_payload(payload: dict) -> bool:
        """Valida se payload tem estrutura esperada."""
        try:
            data = payload.get("data", {})
            hourly = data.get("hourly", {})

            if not isinstance(hourly, dict):
                return False

            if "time" not in hourly or not hourly["time"]:
                return False

            return True
        except Exception as e:
            logger.error(f"Payload validation failed: {e}")
            return False
