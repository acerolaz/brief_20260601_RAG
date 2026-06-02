"""In-memory signal store adapter — implements SignalStorePort.

Suitable for development and testing. Replace with a DB-backed implementation
(e.g. PostgreSQL via SQLAlchemy) for production workloads.
"""
from __future__ import annotations

import asyncio
from collections import deque

from src.domain.entities import Signal


class InMemorySignalStoreAdapter:
    """Thread-safe, in-process signal store backed by a bounded deque.

    Args:
        max_size: Maximum number of signals retained in memory (FIFO eviction).
    """

    def __init__(self, max_size: int = 1000) -> None:
        self._store: deque[Signal] = deque(maxlen=max_size)
        self._lock = asyncio.Lock()

    async def save(self, signal: Signal) -> None:
        """Append *signal* to the in-memory store."""
        async with self._lock:
            self._store.append(signal)

    async def list_recent(self, limit: int = 50) -> list[Signal]:
        """Return up to *limit* most recently received signals."""
        async with self._lock:
            signals = list(self._store)
        # Sort descending by received_at and take the top `limit`
        signals.sort(key=lambda s: s.received_at, reverse=True)
        return signals[:limit]

    async def clear(self) -> None:
        """Erase all signals (testing / data erasure)."""
        async with self._lock:
            self._store.clear()

