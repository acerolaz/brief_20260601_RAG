"""Unit tests for InMemorySignalStoreAdapter."""
from __future__ import annotations

import pytest

from src.domain.entities import Signal, SignalType
from src.infrastructure.adapters.in_memory_signal_store import InMemorySignalStoreAdapter


def _make_signal(n: int) -> Signal:
    return Signal(id=f"sig-{n:03d}", signal_type=SignalType.RSS, topic=f"topic-{n}")


@pytest.mark.asyncio
async def test_save_and_list_recent():
    store = InMemorySignalStoreAdapter()
    s1 = _make_signal(1)
    s2 = _make_signal(2)
    await store.save(s1)
    await store.save(s2)

    recent = await store.list_recent(limit=10)
    assert len(recent) == 2
    ids = {s.id for s in recent}
    assert "sig-001" in ids
    assert "sig-002" in ids


@pytest.mark.asyncio
async def test_list_recent_respects_limit():
    store = InMemorySignalStoreAdapter()
    for i in range(10):
        await store.save(_make_signal(i))
    recent = await store.list_recent(limit=3)
    assert len(recent) == 3


@pytest.mark.asyncio
async def test_max_size_evicts_oldest():
    store = InMemorySignalStoreAdapter(max_size=3)
    for i in range(5):
        await store.save(_make_signal(i))
    recent = await store.list_recent(limit=10)
    assert len(recent) == 3  # deque evicted the two oldest


@pytest.mark.asyncio
async def test_clear_empties_store():
    store = InMemorySignalStoreAdapter()
    await store.save(_make_signal(1))
    await store.clear()
    assert await store.list_recent() == []

