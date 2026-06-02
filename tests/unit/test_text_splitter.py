"""Unit tests for the LangChain text splitter adapter (no API calls)."""
from __future__ import annotations

from src.infrastructure.langchain.splitters.text_splitter import LangChainTextSplitterAdapter


def test_split_produces_chunks():
    splitter = LangChainTextSplitterAdapter(chunk_size=100, chunk_overlap=10)
    text = "LangChain is a framework. " * 30  # ~780 chars → multiple chunks
    chunks = splitter.split("doc-1", text)

    assert len(chunks) >= 2
    for i, chunk in enumerate(chunks):
        assert chunk.source_id == "doc-1"
        assert chunk.chunk_index == i
        assert chunk.text.strip()
        assert chunk.id  # non-empty deterministic ID


def test_split_empty_text_returns_empty():
    splitter = LangChainTextSplitterAdapter()
    assert splitter.split("doc-1", "") == []
    assert splitter.split("doc-1", "   ") == []


def test_chunk_ids_are_deterministic():
    splitter = LangChainTextSplitterAdapter(chunk_size=200, chunk_overlap=0)
    text = "Reproducible chunk. " * 20
    run1 = splitter.split("doc-x", text)
    run2 = splitter.split("doc-x", text)
    assert [c.id for c in run1] == [c.id for c in run2]

