"""Inbound Ports — Driving Port contracts (use-case interfaces).

These ``Protocol`` classes define what the application *exposes* to the outside world
(HTTP controllers, CLI, tests). Infrastructure adapters call these ports; they never
reach into use-case implementation details directly.
"""
from __future__ import annotations

from typing import Protocol

from src.application.dtos import (
    IngestDocumentRequest,
    IngestDocumentResponse,
    IngestFreshnessSignalRequest,
    IngestFreshnessSignalResponse,
    QueryRequest,
    QueryResponse,
)


class IngestStructuredDocumentUseCase(Protocol):
    """Port: ingest a deep-knowledge asset (PDF, whitepaper) into the vector store."""

    async def execute(self, request: IngestDocumentRequest) -> IngestDocumentResponse:
        ...


class IngestFreshnessSignalUseCase(Protocol):
    """Port: ingest a high-frequency freshness signal (webhook / RSS)."""

    async def execute(self, request: IngestFreshnessSignalRequest) -> IngestFreshnessSignalResponse:
        ...


class QueryAssistantUseCase(Protocol):
    """Port: answer a user question using retrieved context."""

    async def execute(self, request: QueryRequest) -> QueryResponse:
        ...

