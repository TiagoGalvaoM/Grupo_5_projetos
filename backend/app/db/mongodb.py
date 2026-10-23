"""
Conexão e operações com MongoDB Atlas (camada RAW).
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class MongoDBManager:
    """Gerenciador de conexão com MongoDB Atlas."""

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self):
        """Conecta ao MongoDB Atlas."""
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_uri)
            self.db = self.client[settings.mongodb_database]

            # Testa conexão
            await self.client.admin.command("ping")
            logger.info(
                f"MongoDB connected successfully to database: {settings.mongodb_database}"
            )

            # Cria índices
            await self._create_indexes()

        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise

    async def disconnect(self):
        """Desconecta do MongoDB Atlas."""
        if self.client:
            self.client.close()
            logger.info("MongoDB disconnected")

    async def _create_indexes(self):
        """Cria índices na coleção raw_ingestions."""
        collection = self.db.raw_ingestions

        # Índice por fonte e timestamp
        await collection.create_index([("source", 1), ("collected_at", -1)])

        # Índice por hash (deduplicação)
        await collection.create_index([("payload_hash", 1)], unique=True)

        # Índice por status
        await collection.create_index([("status", 1), ("collected_at", -1)])

        # Índice por período de referência
        await collection.create_index([("reference_period.start", 1)])

        logger.info("MongoDB indexes created")

    def get_collection(self, name: str):
        """Retorna uma coleção do banco."""
        if self.db is None:
            raise RuntimeError("MongoDB not connected")
        return self.db[name]


# Instância global
mongodb = MongoDBManager()


async def get_mongodb() -> AsyncIOMotorDatabase:
    """Dependency para FastAPI."""
    if mongodb.db is None:
        raise RuntimeError("MongoDB not connected")
    return mongodb.db
