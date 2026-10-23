"""
Script para popular dados iniciais no banco (fontes, indicadores, territórios).
Executar após criar as migrações.
"""
import asyncio
import sys
import os

# Adiciona diretório pai ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres import AsyncSessionLocal
from app.domain.models import DataSource, Indicator, Territory
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


async def seed_data_sources(db: AsyncSession):
    """Cria fontes de dados."""
    sources = [
        DataSource(
            name="open_meteo",
            provider="Open-Meteo",
            source_type="api",
            url="https://api.open-meteo.com",
            update_frequency="hourly",
            active=True,
        ),
        DataSource(
            name="infodengue",
            provider="InfoDengue",
            source_type="api",
            url="https://info.dengue.mat.br/api",
            update_frequency="weekly",
            active=True,
        ),
    ]

    for source in sources:
        db.add(source)

    await db.commit()
    logger.info(f"Created {len(sources)} data sources")


async def seed_indicators(db: AsyncSession):
    """Cria indicadores meteorológicos e epidemiológicos."""
    indicators = [
        # Meteorologia
        Indicator(
            code="temp_2m",
            name="Temperatura a 2m",
            category="meteorology",
            unit="celsius",
            description="Temperatura do ar a 2 metros de altura",
        ),
        Indicator(
            code="precipitation",
            name="Precipitação",
            category="meteorology",
            unit="mm",
            description="Precipitação acumulada",
        ),
        Indicator(
            code="rain",
            name="Chuva",
            category="meteorology",
            unit="mm",
            description="Chuva",
        ),
        Indicator(
            code="precip_prob",
            name="Probabilidade de Precipitação",
            category="meteorology",
            unit="percent",
            description="Probabilidade de ocorrer precipitação",
        ),
        Indicator(
            code="humidity",
            name="Umidade Relativa",
            category="meteorology",
            unit="percent",
            description="Umidade relativa do ar",
        ),
        Indicator(
            code="wind_speed",
            name="Velocidade do Vento",
            category="meteorology",
            unit="km/h",
            description="Velocidade do vento a 10 metros de altura",
        ),
        Indicator(
            code="weather_code",
            name="Código Meteorológico",
            category="meteorology",
            unit="wmo_code",
            description="Código meteorológico WMO",
        ),
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

    for indicator in indicators:
        db.add(indicator)

    await db.commit()
    logger.info(f"Created {len(indicators)} indicators")


async def seed_territories(db: AsyncSession):
    """Cria territórios."""
    territories = [
        Territory(
            code="2611606",  # Código IBGE Recife
            name="Recife",
            type="city",
            latitude=-8.05,
            longitude=-34.9,
        ),
    ]

    for territory in territories:
        db.add(territory)

    await db.commit()
    logger.info(f"Created {len(territories)} territories")


async def main():
    """Executa seed de todos os dados iniciais."""
    logger.info("Starting database seed...")

    async with AsyncSessionLocal() as db:
        try:
            await seed_data_sources(db)
            await seed_indicators(db)
            await seed_territories(db)

            logger.info("Database seed completed successfully!")

        except Exception as e:
            logger.error(f"Seed failed: {e}", exc_info=True)
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
