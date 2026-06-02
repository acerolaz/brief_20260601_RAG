"""Typed tool adapters — infrastructure adapter layer.

Tools are registered with agents via ``llm.bind_tools([...])`` or passed to
``create_react_agent``. Each tool validates inputs and outputs strictly.
The domain/application layers never import from this module.
"""
from __future__ import annotations

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import StructuredTool


def build_document_search_tool(retriever: BaseRetriever) -> StructuredTool:
    """Return a document_search tool wired to a live retriever.

    The tool is injected with the retriever at build time so no side-effectful
    infrastructure is imported at module load time.

    Args:
        retriever: A LangChain ``BaseRetriever`` (e.g. from ``build_retriever``).

    Returns:
        A :class:`~langchain_core.tools.StructuredTool` ready to pass to an agent.
    """

    def _search(query: str) -> str:
        docs: list[Document] = retriever.invoke(query)
        if not docs:
            return "No relevant documents found."
        return "\n\n".join(
            f"[{doc.metadata.get('source_id', 'unknown')}] {doc.page_content}" for doc in docs
        )

    return StructuredTool.from_function(
        func=_search,
        name="document_search",
        description=(
            "Search the knowledge base for document passages relevant to a query. "
            "Input: a natural-language query string."
        ),
    )
