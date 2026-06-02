"""Global test fixtures shared across unit and acceptance test suites."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.domain.entities import Chunk


@pytest.fixture()
def sample_chunks() -> list[Chunk]:
    return [
        Chunk(id="c1", text="LangChain is a framework for building LLM apps.", source_id="doc-1", chunk_index=0),
        Chunk(id="c2", text="It supports RAG, chains, and agents.", source_id="doc-1", chunk_index=1),
    ]


@pytest.fixture()
def mock_vector_store(sample_chunks):
    store = AsyncMock()
    store.upsert_chunks.return_value = None
    store.similarity_search.return_value = sample_chunks
    store.delete_chunks.return_value = None
    return store


@pytest.fixture()
def mock_ai_assistant():
    assistant = AsyncMock()
    assistant.answer.return_value = "LangChain is a framework for LLM applications."
    return assistant


@pytest.fixture()
def mock_signal_store():
    store = AsyncMock()
    store.save.return_value = None
    store.list_recent.return_value = []
    return store


@pytest.fixture()
def mock_splitter(sample_chunks):
    splitter = MagicMock()
    splitter.split.return_value = sample_chunks
    return splitter


