"""Pydantic HTTP request/response schemas for FastAPI endpoints.

These are *separate* from the application-layer DTOs: they handle HTTP-level
concerns (field aliases, examples, validation error formatting).
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class IngestDocumentHTTPRequest(BaseModel):
    document_id: str = Field(..., examples=["doc-001"])
    title: str = Field(..., examples=["LangChain Overview"])
    content: str = Field(..., examples=["LangChain is a framework..."])
    source_url: str | None = Field(None, examples=["https://example.com/doc.pdf"])
    metadata: dict = Field(default_factory=dict)


class IngestDocumentHTTPResponse(BaseModel):
    document_id: str
    chunks_stored: int


class IngestSignalHTTPRequest(BaseModel):
    signal_id: str = Field(..., examples=["sig-001"])
    signal_type: str = Field(..., examples=["rss"])
    topic: str = Field(..., examples=["LangChain release"])
    payload: dict = Field(default_factory=dict)


class IngestSignalHTTPResponse(BaseModel):
    signal_id: str
    acknowledged: bool


class QueryHTTPRequest(BaseModel):
    question: str = Field(..., examples=["What is RAG?"])
    conversation_id: str | None = None
    top_k: int = Field(4, ge=1, le=20)


class QueryHTTPResponse(BaseModel):
    answer: str
    source_ids: list[str] = []

