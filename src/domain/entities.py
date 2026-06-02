"""Domain entities — pure Python dataclasses, zero external dependencies."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class SignalType(str, Enum):
    WEBHOOK = "webhook"
    RSS = "rss"


@dataclass(frozen=True)
class Chunk:
    """A piece of text produced by splitting a source document."""

    id: str
    text: str
    source_id: str
    chunk_index: int
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Document:
    """A source document to be ingested into the knowledge base."""

    id: str
    title: str
    content: str
    source_url: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Signal:
    """A freshness signal (webhook event or RSS entry) that may invalidate cache
    or flag a trending topic in the knowledge base."""

    id: str
    signal_type: SignalType
    topic: str
    payload: dict = field(default_factory=dict)
    received_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

