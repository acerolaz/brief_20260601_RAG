"""Outbound Ports — Driven Port SPIs (Service Provider Interfaces).

These ``Protocol`` classes define what the application *requires* from infrastructure.
Concrete implementations live in ``src/infrastructure/adapters/``.
The application core depends only on these abstractions — never on concrete classes.
"""
from __future__ import annotations

from typing import Protocol

from src.domain.entities import Chunk, Signal


class DocumentSplitterPort(Protocol):
    """SPI: split a raw text document into indexable chunks."""

    def split(self, document_id: str, text: str) -> list[Chunk]:
        """Return a list of :class:`~src.domain.entities.Chunk` objects.

        Args:
            document_id: ID of the source document (propagated to each chunk).
            text: Full raw text of the document.
        """
        ...


class SignalStorePort(Protocol):
    """SPI: persist freshness signals for downstream consumers."""

    async def save(self, signal: Signal) -> None:
        """Persist *signal* to the backing store."""
        ...

    async def list_recent(self, limit: int = 50) -> list[Signal]:
        """Return the most recent *limit* signals ordered by received_at descending."""
        ...


class VectorStorePort(Protocol):
    """SPI: persist and retrieve document chunks from a vector store."""

    async def upsert_chunks(self, chunks: list[Chunk]) -> None:
        """Store or update a list of text chunks."""
        ...

    async def similarity_search(
        self, query: str, top_k: int = 4, metadata_filter: dict | None = None
    ) -> list[Chunk]:
        """Return the top-k most relevant chunks for *query*."""
        ...

    async def delete_chunks(self, ids: list[str]) -> None:
        """Remove chunks by their IDs."""
        ...


class AIAssistantPort(Protocol):
    """SPI: generate a natural-language answer given a question and context."""

    async def answer(self, question: str, context: str) -> str:
        """Generate an answer grounded in *context*."""
        ...


class ScraperPort(Protocol):
    """SPI: fetch and parse the text content of a URL."""

    async def scrape(self, url: str) -> str:
        """Return the extracted text from *url*.

        Raises:
            ScrapingError: If the URL cannot be fetched or parsed.
        """
        ...

