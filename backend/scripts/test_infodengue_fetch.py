"""
Script para testar fetch da API InfoDengue e inspecionar os dados.
"""
import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ingestion.infodengue_connector import InfoDengueConnector
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


async def main():
    """Testa fetch da API InfoDengue."""
    logger.info("Testing InfoDengue API fetch...")

    connector = InfoDengueConnector()

    # Busca dados de 4 semanas para teste rápido
    result = await connector.fetch(weeks_back=4)

    print("\n" + "=" * 80)
    print("INFODENGUE FETCH RESULT")
    print("=" * 80)
    print(json.dumps(result, indent=2, default=str))
    print("=" * 80 + "\n")

    # Testa validador
    from app.transformation.infodengue_transformer import InfoDengueTransformer
    transformer = InfoDengueTransformer()

    is_valid = transformer.validate_payload(result)
    print(f"Payload is valid: {is_valid}")

    # Mostra estrutura dos dados
    data = result.get("data", {})
    for disease, records in data.items():
        if isinstance(records, list):
            print(f"\n{disease}: {len(records)} records")
            if records:
                print(f"First record keys: {records[0].keys()}")
        elif isinstance(records, dict):
            print(f"\n{disease}: {records}")


if __name__ == "__main__":
    asyncio.run(main())
