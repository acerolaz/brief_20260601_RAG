"""Acceptance tests — black-box API contract verification via FastAPI TestClient.

Requires a running application stack (mocked adapters injected via DI overrides).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from src.infrastructure.api.main import app
from src.infrastructure.config.container import (
    get_ingest_freshness_use_case,
    get_ingest_structured_use_case,
    get_query_assistant_use_case,
)
from src.application.dtos import (
    IngestDocumentResponse,
    IngestFreshnessSignalResponse,
    QueryResponse,
)


@pytest.fixture()
def client(mock_vector_store, mock_ai_assistant, mock_signal_store, mock_splitter):
    """TestClient with all use-case dependencies overridden with mocks."""
    from src.application.use_cases.ingest_structured import IngestStructuredDocumentInteractor
    from src.application.use_cases.ingest_freshness import IngestFreshnessSignalInteractor
    from src.application.use_cases.query_assistant import QueryAssistantInteractor

    app.dependency_overrides[get_ingest_structured_use_case] = lambda: IngestStructuredDocumentInteractor(
        vector_store=mock_vector_store,
        splitter=mock_splitter,
    )
    app.dependency_overrides[get_ingest_freshness_use_case] = lambda: IngestFreshnessSignalInteractor(
        signal_store=mock_signal_store,
    )
    app.dependency_overrides[get_query_assistant_use_case] = lambda: QueryAssistantInteractor(
        vector_store=mock_vector_store,
        ai_assistant=mock_ai_assistant,
    )

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ingest_structured_document(client):
    payload = {
        "document_id": "doc-001",
        "title": "Test",
        "content": "Some content to ingest " * 10,
    }
    response = client.post("/api/v1/ingest/structured/", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["document_id"] == "doc-001"
    assert isinstance(body["chunks_stored"], int)


def test_ingest_freshness_signal(client):
    payload = {
        "signal_id": "sig-001",
        "signal_type": "rss",
        "topic": "LangChain 0.3 released",
        "payload": {"url": "https://example.com/feed"},
    }
    response = client.post("/api/v1/ingest/freshness/", json=payload)
    assert response.status_code == 202
    assert response.json()["acknowledged"] is True


def test_query_endpoint(client):
    payload = {"question": "What is LangChain?", "top_k": 2}
    response = client.post("/api/v1/query", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
    assert isinstance(body["source_ids"], list)


def test_query_missing_question_returns_422(client):
    response = client.post("/api/v1/query", json={"top_k": 2})
    assert response.status_code == 422
