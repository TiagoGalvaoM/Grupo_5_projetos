"""
Transformador de dados epidemiológicos (InfoDengue).
"""
from datetime import datetime
from typing import List, Dict, Any
from app.core.logging import get_logger

logger = get_logger(__name__)


class InfoDengueTransformer:
    """Transforma dados brutos da API InfoDengue em modelo interno."""

    # Mapeamento de campos InfoDengue para indicadores internos
    INDICATOR_MAPPING = {
        "casos_est": {
            "dengue": "dengue_casos_est",
            "chikungunya": "chik_casos_est",
            "zika": "zika_casos_est",
        },
        "casos": {
            "dengue": "dengue_casos",
            "chikungunya": "chik_casos",
            "zika": "zika_casos",
        },
        "nivel": {
            "dengue": "dengue_nivel_alerta",
            "chikungunya": "chik_nivel_alerta",
            "zika": "zika_nivel_alerta",
        },
        "temperatura_media": "temp_media_epi",
        "umidade_media": "umidade_media_epi",
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
        collected_at = datetime.utcnow()

        data = raw_payload.get("data", {})

        # Processar cada doença
        for disease, records in data.items():
            if isinstance(records, dict) and "error" in records:
                logger.warning(
                    f"Skipping {disease} due to error: {records['error']}",
                    extra={"disease": disease},
                )
                continue

            if not isinstance(records, list):
                logger.warning(
                    f"Unexpected data format for {disease}",
                    extra={"disease": disease, "type": type(records).__name__},
                )
                continue

            # Processar cada semana epidemiológica
            for record in records:
                # Extrair semana epidemiológica e data
                se = record.get("SE")  # Semana Epidemiológica (formato YYYYWW ou int)
                data_iniSE = record.get("data_iniSE")  # Data início da semana

                if se is None or data_iniSE is None:
                    continue

                # Converter SE para string se vier como int
                se = str(se) if isinstance(se, int) else se

                # Converter data_iniSE para datetime
                try:
                    # data_iniSE pode vir como timestamp Unix em millisegundos ou como string
                    if isinstance(data_iniSE, (int, float)):
                        # Unix timestamp em millisegundos
                        reference_time = datetime.fromtimestamp(data_iniSE / 1000)
                    else:
                        # String no formato YYYY-MM-DD
                        reference_time = datetime.strptime(data_iniSE, "%Y-%m-%d")
                except (ValueError, TypeError, OSError) as e:
                    logger.warning(
                        f"Invalid date format: {data_iniSE}",
                        extra={"error": str(e)},
                    )
                    continue

                # Casos estimados
                casos_est = record.get("casos_est")
                if casos_est is not None:
                    indicator_code = self.INDICATOR_MAPPING["casos_est"].get(disease)
                    if indicator_code and indicator_code in indicator_ids:
                        measurements.append(
                            {
                                "source_id": source_id,
                                "indicator_id": indicator_ids[indicator_code],
                                "territory_id": territory_id,
                                "reference_time": reference_time,
                                "collected_at": collected_at,
                                "value": float(casos_est),
                                "unit": "cases",
                                "raw_ingestion_id": raw_ingestion_id,
                                "metadata": {
                                    "disease": disease,
                                    "epiweek": se,
                                    "epiweek_year": int(se[:4]) if len(se) >= 4 else None,
                                    "epiweek_number": int(se[4:6]) if len(se) >= 6 else None,
                                },
                            }
                        )

                # Casos notificados
                casos = record.get("casos")
                if casos is not None:
                    indicator_code = self.INDICATOR_MAPPING["casos"].get(disease)
                    if indicator_code and indicator_code in indicator_ids:
                        measurements.append(
                            {
                                "source_id": source_id,
                                "indicator_id": indicator_ids[indicator_code],
                                "territory_id": territory_id,
                                "reference_time": reference_time,
                                "collected_at": collected_at,
                                "value": float(casos),
                                "unit": "cases",
                                "raw_ingestion_id": raw_ingestion_id,
                                "metadata": {
                                    "disease": disease,
                                    "epiweek": se,
                                    "epiweek_year": int(se[:4]) if len(se) >= 4 else None,
                                    "epiweek_number": int(se[4:6]) if len(se) >= 6 else None,
                                },
                            }
                        )

                # Nível de alerta (1=verde, 2=amarelo, 3=laranja, 4=vermelho)
                nivel = record.get("nivel")
                if nivel is not None:
                    indicator_code = self.INDICATOR_MAPPING["nivel"].get(disease)
                    if indicator_code and indicator_code in indicator_ids:
                        measurements.append(
                            {
                                "source_id": source_id,
                                "indicator_id": indicator_ids[indicator_code],
                                "territory_id": territory_id,
                                "reference_time": reference_time,
                                "collected_at": collected_at,
                                "value": float(nivel),
                                "unit": "level",
                                "raw_ingestion_id": raw_ingestion_id,
                                "metadata": {
                                    "disease": disease,
                                    "epiweek": se,
                                    "epiweek_year": int(se[:4]) if len(se) >= 4 else None,
                                    "epiweek_number": int(se[4:6]) if len(se) >= 6 else None,
                                    "nivel_color": self._get_nivel_color(nivel),
                                },
                            }
                        )

                # Temperatura média (se disponível)
                temp_media = record.get("tempmed")
                if temp_media is not None:
                    indicator_code = "temp_media_epi"
                    if indicator_code in indicator_ids:
                        measurements.append(
                            {
                                "source_id": source_id,
                                "indicator_id": indicator_ids[indicator_code],
                                "territory_id": territory_id,
                                "reference_time": reference_time,
                                "collected_at": collected_at,
                                "value": float(temp_media),
                                "unit": "celsius",
                                "raw_ingestion_id": raw_ingestion_id,
                                "metadata": {
                                    "epiweek": se,
                                    "source_disease": disease,
                                },
                            }
                        )

                # Umidade média (se disponível)
                umid_media = record.get("umidmed")
                if umid_media is not None:
                    indicator_code = "umidade_media_epi"
                    if indicator_code in indicator_ids:
                        measurements.append(
                            {
                                "source_id": source_id,
                                "indicator_id": indicator_ids[indicator_code],
                                "territory_id": territory_id,
                                "reference_time": reference_time,
                                "collected_at": collected_at,
                                "value": float(umid_media),
                                "unit": "percent",
                                "raw_ingestion_id": raw_ingestion_id,
                                "metadata": {
                                    "epiweek": se,
                                    "source_disease": disease,
                                },
                            }
                        )

        logger.info(
            f"Transformed {len(measurements)} epidemiological measurements",
            extra={"diseases": list(data.keys()), "total_measurements": len(measurements)},
        )

        return measurements

    @staticmethod
    def _get_nivel_color(nivel: int) -> str:
        """Converte código de nível para cor do alerta."""
        colors = {1: "verde", 2: "amarelo", 3: "laranja", 4: "vermelho"}
        return colors.get(nivel, "desconhecido")

    @staticmethod
    def validate_payload(payload: dict) -> bool:
        """Valida se payload tem estrutura esperada."""
        try:
            data = payload.get("data", {})

            if not isinstance(data, dict):
                return False

            # Verifica se há pelo menos uma doença com dados válidos
            has_valid_data = False
            for disease, records in data.items():
                if isinstance(records, list) and len(records) > 0:
                    has_valid_data = True
                    break

            return has_valid_data

        except Exception as e:
            logger.error(f"Payload validation failed: {e}")
            return False
