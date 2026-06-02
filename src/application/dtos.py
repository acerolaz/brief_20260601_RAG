"""Application-layer DTOs — strict request/response shapes for use-case boundaries.

These are Pydantic models used *inside* the application core. They are distinct from
the infrastructure-layer HTTP schemas (``src/infrastructure/api/schemas.py``).
"""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


# ── Inbound DTOs (driving side) ───────────────────────────────────────────────

class IngestDocumentRequest(BaseModel):
    """Request to ingest a structured document (PDF, whitepaper, etc.)."""

    document_id: str
    title: str
    # content may be blank — the splitter adapter handles empty text gracefully
    content: str
    source_url: str | None = None
    metadata: dict = Field(default_factory=dict)

    @field_validator("document_id", "title")
    @classmethod
    def must_be_non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field must not be empty or whitespace.")
        return v


class IngestFreshnessSignalRequest(BaseModel):
    """Request to ingest a freshness signal (RSS entry or webhook payload)."""

    signal_id: str
    signal_type: str          # "webhook" | "rss"
    topic: str
    payload: dict = Field(default_factory=dict)


class QueryRequest(BaseModel):
    """Request to query the RAG assistant."""

    question: str
    conversation_id: str | None = None
    top_k: int = 4

    @field_validator("question")
    @classmethod
    def question_must_be_non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Question must not be empty.")
        return v


# ── Outbound DTOs (driven side) ───────────────────────────────────────────────

class IngestDocumentResponse(BaseModel):
    document_id: str
    chunks_stored: int


class IngestFreshnessSignalResponse(BaseModel):
    signal_id: str
    acknowledged: bool


class QueryResponse(BaseModel):
    answer: str
    source_ids: list[str] = []

