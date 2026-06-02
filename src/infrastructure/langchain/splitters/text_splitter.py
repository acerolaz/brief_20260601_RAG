"""LangChain text splitter adapter — implements DocumentSplitterPort.

Uses RecursiveCharacterTextSplitter for semantically aware splitting.
Lives in infrastructure because it depends on the LangChain framework.
"""
from __future__ import annotations

import hashlib

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.domain.entities import Chunk


class LangChainTextSplitterAdapter:
    """Driven adapter: splits raw text into domain Chunk objects.

    Args:
        chunk_size: Target size in characters per chunk (default 800).
        chunk_overlap: Overlap between consecutive chunks (default 100).
    """

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def split(self, document_id: str, text: str) -> list[Chunk]:
        """Split *text* into :class:`~src.domain.entities.Chunk` objects.

        Args:
            document_id: Source document ID propagated to each chunk.
            text: Full raw text of the document.

        Returns:
            Ordered list of Chunk objects; empty list if text is blank.
        """
        if not text or not text.strip():
            return []

        pieces: list[str] = self._splitter.split_text(text)
        return [
            Chunk(
                id=hashlib.sha256(f"{document_id}:{i}:{piece[:40]}".encode()).hexdigest()[:16],
                text=piece,
                source_id=document_id,
                chunk_index=i,
            )
            for i, piece in enumerate(pieces)
        ]

