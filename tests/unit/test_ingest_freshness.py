"""Unit tests for IngestFreshnessSignalInteractor."""
from __future__ import annotations

import pytest

from src.application.dtos import IngestFreshnessSignalRequest
from src.application.use_cases.ingest_freshness import IngestFreshnessSignalInteractor


@pytest.mark.asyncio
async def test_valid_rss_signal_is_saved_and_acknowledged(mock_signal_store):
    interactor = IngestFreshnessSignalInteractor(signal_store=mock_signal_store)
    request = IngestFreshnessSignalRequest(
        signal_id="sig-001",
        signal_type="rss",
        topic="LangChain release",
        payload={"url": "https://example.com/feed"},
    )
    response = await interactor.execute(request)

    assert response.acknowledged is True
    assert response.signal_id == "sig-001"
    mock_signal_store.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_valid_webhook_signal_is_acknowledged(mock_signal_store):
    interactor = IngestFreshnessSignalInteractor(signal_store=mock_signal_store)
    request = IngestFreshnessSignalRequest(
        signal_id="sig-002",
        signal_type="webhook",
        topic="New PR merged",
        payload={"repo": "langchain-ai/langchain"},
    )
    response = await interactor.execute(request)
    assert response.acknowledged is True


@pytest.mark.asyncio
async def test_invalid_signal_type_not_saved(mock_signal_store):
    interactor = IngestFreshnessSignalInteractor(signal_store=mock_signal_store)
    request = IngestFreshnessSignalRequest(
        signal_id="sig-003",
        signal_type="unknown_type",
        topic="Something",
    )
    response = await interactor.execute(request)

    assert response.acknowledged is False
    mock_signal_store.save.assert_not_awaited()
