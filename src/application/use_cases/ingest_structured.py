"""Use case: ingest a structured document (PDF, whitepaper) into the vector store.

This interactor implements :class:`~src.application.ports.inbound.IngestStructuredDocumentUseCase`.
It depends only on outbound ports — never on concrete infrastructure classes.
"""
from __future__ import annotations

from src.application.dtos import IngestDocumentRequest, IngestDocumentResponse
from src.application.ports.outbound import DocumentSplitterPort, VectorStorePort


class IngestStructuredDocumentInteractor:
    """Ingest a structured document: split → embed → upsert into the vector store."""

    def __init__(
        self,
        vector_store: VectorStorePort,
        splitter: DocumentSplitterPort,
    ) -> None:
        self._vector_store = vector_store
        self._splitter = splitter

    async def execute(self, request: IngestDocumentRequest) -> IngestDocumentResponse:
        chunks = self._splitter.split(request.document_id, request.content)

        if not chunks:
            return IngestDocumentResponse(document_id=request.document_id, chunks_stored=0)

        await self._vector_store.upsert_chunks(chunks)
        return IngestDocumentResponse(
            document_id=request.document_id,
            chunks_stored=len(chunks),
        )
