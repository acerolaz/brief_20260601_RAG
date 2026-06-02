"""Database initialisation script.

Creates the pgvector extension and the LangChain PGVector collection tables.
Run once before starting the API:

    python -m src.infrastructure.config.init_db
"""
from __future__ import annotations

import asyncio
import logging

import asyncpg

from src.infrastructure.config.settings import get_settings

logger = logging.getLogger(__name__)


async def init_db() -> None:
    settings = get_settings()
    dsn = settings.database_url.replace("+asyncpg", "")  # asyncpg native DSN

    logger.info("Connecting to %s …", settings.postgres_server)
    conn: asyncpg.Connection = await asyncpg.connect(dsn)

    try:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        logger.info("pgvector extension ready.")

        # LangChain PGVector creates its own tables on first use, but we ensure
        # the schema exists so health-checks pass before the first document ingestion.
        # Dimension 1536 matches text-embedding-3-small / text-embedding-ada-002.
        # Update if switching to a model with a different output dimension.
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS langchain_pg_collection (
                uuid      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name      VARCHAR NOT NULL UNIQUE,
                cmetadata JSONB
            );
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS langchain_pg_embedding (
                id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                collection_id UUID REFERENCES langchain_pg_collection(uuid) ON DELETE CASCADE,
                embedding     VECTOR(1536),
                document      TEXT,
                cmetadata     JSONB,
                custom_id     TEXT
            );
            """
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS langchain_pg_embedding_idx "
            "ON langchain_pg_embedding USING ivfflat (embedding vector_cosine_ops) "
            "WITH (lists = 100);"
        )
        logger.info("LangChain PGVector tables and index ready.")
    finally:
        await conn.close()


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    asyncio.run(init_db())


