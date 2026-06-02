"""Unit tests for QueryAssistantInteractor — all I/O mocked, no network calls."""
from __future__ import annotations

import pytest

from src.application.dtos import QueryRequest
from src.application.use_cases.query_assistant import QueryAssistantInteractor


@pytest.mark.asyncio
async def test_query_returns_answer(mock_vector_store, mock_ai_assistant):
    interactor = QueryAssistantInteractor(
        vector_store=mock_vector_store,
        ai_assistant=mock_ai_assistant,
    )
    response = await interactor.execute(QueryRequest(question="What is LangChain?"))

    assert response.answer == "LangChain is a framework for LLM applications."
    assert "doc-1" in response.source_ids
    mock_vector_store.similarity_search.assert_awaited_once()
    mock_ai_assistant.answer.assert_awaited_once()


@pytest.mark.asyncio
async def test_query_no_chunks_returns_fallback(mock_ai_assistant):
    from unittest.mock import AsyncMock

    empty_store = AsyncMock()
    empty_store.similarity_search.return_value = []

    interactor = QueryAssistantInteractor(
        vector_store=empty_store,
        ai_assistant=mock_ai_assistant,
    )
    response = await interactor.execute(QueryRequest(question="Unknown topic?"))

    assert "don't have enough information" in response.answer
    mock_ai_assistant.answer.assert_not_awaited()

