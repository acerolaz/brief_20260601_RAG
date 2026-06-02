"""Domain-level exceptions — raised by use cases and domain logic."""
from __future__ import annotations


class DocumentNotFoundError(Exception):
    """Raised when a requested document does not exist in the store."""


class DuplicateDocumentError(Exception):
    """Raised when a document with the same ID is already ingested."""


class ScrapingError(Exception):
    """Raised when the scraper fails to retrieve or parse a URL."""


class AIAssistantError(Exception):
    """Raised when the AI assistant fails to generate a response."""


class VectorStoreError(Exception):
    """Raised when the vector store encounters an unexpected error."""

