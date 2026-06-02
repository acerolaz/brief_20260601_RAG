"""pgvector adapter — implements VectorStorePort using PostgreSQL + pgvector.

Uses LangChain's PGVector integration with its native async methods
(aadd_documents, asimilarity_search, adelete) to avoid blocking the event loop.
"""
from __future__ import annotations

from langchain_core.documents import Document as LCDocument
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

from src.domain.entities import Chunk
from src.domain.exceptions import VectorStoreError


class PgVectorStoreAdapter:
    """Driven adapter: persists and retrieves chunks via PostgreSQL + pgvector."""

    def __init__(
        self,
        database_url: str,
        embedding_model: str,
        openai_api_key: str,
    ) -> None:
        self._embeddings = OpenAIEmbeddings(model=embedding_model, api_key=openai_api_key)
        self._store = PGVector(
            embeddings=self._embeddings,
            collection_name="tech_watch_chunks",
            connection=database_url,
            use_jsonb=True,
        )

    async def upsert_chunks(self, chunks: list[Chunk]) -> None:
        """Embed and upsert chunks into pgvector (async)."""
        try:
            documents = [
                LCDocument(
                    page_content=c.text,
                    metadata={
                        "source_id": c.source_id,
                        "chunk_index": c.chunk_index,
                        **c.metadata,
                    },
                )
                for c in chunks
            ]
            ids = [c.id for c in chunks]
            await self._store.aadd_documents(documents=documents, ids=ids)
        except Exception as exc:
            raise VectorStoreError(f"Failed to upsert chunks: {exc}") from exc

    async def similarity_search(
        self, query: str, top_k: int = 4, metadata_filter: dict | None = None
    ) -> list[Chunk]:
        """Return the top-k most relevant chunks for *query* (async)."""
        try:
            kwargs: dict = {"k": top_k}
            if metadata_filter:
                kwargs["filter"] = metadata_filter
            results = await self._store.asimilarity_search(query, **kwargs)
            return [
                Chunk(
                    id=doc.metadata.get("id", ""),
                    text=doc.page_content,
                    source_id=doc.metadata.get("source_id", ""),
                    chunk_index=doc.metadata.get("chunk_index", 0),
                    metadata=doc.metadata,
                )
                for doc in results
            ]
        except Exception as exc:
            raise VectorStoreError(f"Similarity search failed: {exc}") from exc

    async def delete_chunks(self, ids: list[str]) -> None:
        """Remove chunks by ID (async)."""
        try:
            await self._store.adelete(ids=ids)
        except Exception as exc:
            raise VectorStoreError(f"Failed to delete chunks: {exc}") from exc
