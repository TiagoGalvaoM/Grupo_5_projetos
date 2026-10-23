"""
Script para adicionar fonte InfoDengue e indicadores epidemiológicos.
"""
import asyncio
import sys
import os

# Adiciona diretório pai ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.postgres import AsyncSessionLocal
from app.domain.models import DataSource, Indicator
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


async def add_infodengue_source(db: AsyncSession):
    """Adiciona fonte InfoDengue se não existir."""
    # Verifica se já existe
    result = await db.execute(select(DataSource).where(DataSource.name == "infodengue"))
    existing = result.scalar_one_or_none()

    if existing:
        logger.info("InfoDengue source already exists, skipping")
        return

    source = DataSource(
        name="infodengue",
        provider="InfoDengue",
        source_type="api",
        url="https://info.dengue.mat.br/api",
        update_frequency="weekly",
        active=True,
    )

    db.add(source)
    await db.commit()
    logger.info("Created InfoDengue data source")


async def add_epidemiology_indicators(db: AsyncSession):
    """Adiciona indicadores epidemiológicos se não existirem."""
    new_indicators = [
        # Epidemiologia - Dengue
        Indicator(
            code="dengue_casos_est",
            name="Dengue - Casos Estimados",
            category="epidemiology",
            unit="cases",
            description="Casos estimados de dengue por semana epidemiológica",
        ),
        Indicator(
            code="dengue_casos",
            name="Dengue - Casos Notificados",
            category="epidemiology",
            unit="cases",
            description="Casos notificados de dengue no SINAN",
        ),
        Indicator(
            code="dengue_nivel_alerta",
            name="Dengue - Nível de Alerta",
            category="epidemiology",
            unit="level",
            description="Nível de alerta dengue (1=verde, 2=amarelo, 3=laranja, 4=vermelho)",
        ),
        # Epidemiologia - Chikungunya
        Indicator(
            code="chik_casos_est",
            name="Chikungunya - Casos Estimados",
            category="epidemiology",
            unit="cases",
            description="Casos estimados de chikungunya por semana epidemiológica",
        ),
        Indicator(
            code="chik_casos",
            name="Chikungunya - Casos Notificados",
            category="epidemiology",
            unit="cases",
            description="Casos notificados de chikungunya no SINAN",
        ),
        Indicator(
            code="chik_nivel_alerta",
            name="Chikungunya - Nível de Alerta",
            category="epidemiology",
            unit="level",
            description="Nível de alerta chikungunya (1=verde, 2=amarelo, 3=laranja, 4=vermelho)",
        ),
        # Epidemiologia - Zika
        Indicator(
            code="zika_casos_est",
            name="Zika - Casos Estimados",
            category="epidemiology",
            unit="cases",
            description="Casos estimados de zika por semana epidemiológica",
        ),
        Indicator(
            code="zika_casos",
            name="Zika - Casos Notificados",
            category="epidemiology",
            unit="cases",
            description="Casos notificados de zika no SINAN",
        ),
        Indicator(
            code="zika_nivel_alerta",
            name="Zika - Nível de Alerta",
            category="epidemiology",
            unit="level",
            description="Nível de alerta zika (1=verde, 2=amarelo, 3=laranja, 4=vermelho)",
        ),
        # Climatologia Epidemiológica
        Indicator(
            code="temp_media_epi",
            name="Temperatura Média Epidemiológica",
            category="climatology",
            unit="celsius",
            description="Temperatura média da semana epidemiológica (InfoDengue)",
        ),
        Indicator(
            code="umidade_media_epi",
            name="Umidade Média Epidemiológica",
            category="climatology",
            unit="percent",
            description="Umidade média da semana epidemiológica (InfoDengue)",
        ),
    ]

    added_count = 0
    for indicator in new_indicators:
        # Verifica se já existe
        result = await db.execute(
            select(Indicator).where(Indicator.code == indicator.code)
        )
        existing = result.scalar_one_or_none()

        if existing:
            logger.info(f"Indicator {indicator.code} already exists, skipping")
            continue

        db.add(indicator)
        added_count += 1

    await db.commit()
    logger.info(f"Added {added_count} new epidemiology indicators")


async def main():
    """Adiciona fonte InfoDengue e indicadores epidemiológicos."""
    logger.info("Starting epidemiology data addition...")

    async with AsyncSessionLocal() as db:
        try:
            await add_infodengue_source(db)
            await add_epidemiology_indicators(db)

            logger.info("Epidemiology data added successfully!")

        except Exception as e:
            logger.error(f"Addition failed: {e}", exc_info=True)
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
