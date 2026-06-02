"""Unit tests for IngestStructuredDocumentInteractor."""
from __future__ import annotations

import pytest

from src.application.dtos import IngestDocumentRequest
from src.application.use_cases.ingest_structured import IngestStructuredDocumentInteractor


@pytest.mark.asyncio
async def test_ingest_stores_chunks(mock_vector_store, mock_splitter):
    interactor = IngestStructuredDocumentInteractor(
        vector_store=mock_vector_store,
        splitter=mock_splitter,
    )
    request = IngestDocumentRequest(
        document_id="doc-001",
        title="Test Document",
        content="Some meaningful content about LangChain and RAG pipelines.",
    )
    response = await interactor.execute(request)

    assert response.document_id == "doc-001"
    assert response.chunks_stored == 2  # mock_splitter returns 2 sample chunks
    mock_splitter.split.assert_called_once_with("doc-001", request.content)
    mock_vector_store.upsert_chunks.assert_awaited_once()


@pytest.mark.asyncio
async def test_ingest_empty_content_stores_no_chunks(mock_vector_store):
    from unittest.mock import MagicMock

    empty_splitter = MagicMock()
    empty_splitter.split.return_value = []

    interactor = IngestStructuredDocumentInteractor(
        vector_store=mock_vector_store,
        splitter=empty_splitter,
    )
    response = await interactor.execute(
        IngestDocumentRequest(document_id="doc-002", title="Empty", content="   ")
    )
    assert response.chunks_stored == 0
    mock_vector_store.upsert_chunks.assert_not_awaited()
