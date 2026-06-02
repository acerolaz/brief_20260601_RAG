"""Retriever factory adapter — wraps a vectorstore as a LangChain BaseRetriever."""
from __future__ import annotations

from langchain_core.retrievers import BaseRetriever
from langchain_postgres import PGVector


def build_retriever(
    vectorstore: PGVector,
    k: int = 4,
    metadata_filter: dict | None = None,
) -> BaseRetriever:
    """Return a similarity-search retriever from a PGVector vectorstore.

    Args:
        vectorstore: Initialised PGVector store.
        k: Number of documents to retrieve per query.
        metadata_filter: Optional metadata filter dict (pgvector JSONB filter syntax).

    Returns:
        A :class:`~langchain_core.retrievers.BaseRetriever` implementing
        the Runnable interface — ready to compose in an LCEL chain.
    """
    search_kwargs: dict = {"k": k}
    if metadata_filter:
        search_kwargs["filter"] = metadata_filter
    return vectorstore.as_retriever(search_kwargs=search_kwargs)

