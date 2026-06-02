"""Composition Root — manual dependency injection wiring.

This is the ONLY place where concrete infrastructure adapters are instantiated
and wired to application use-case interactors. No other module imports concrete
adapters directly; they depend only on the port interfaces.
"""
from __future__ import annotations

from functools import lru_cache

from langchain_openai import ChatOpenAI

from src.application.use_cases.ingest_freshness import IngestFreshnessSignalInteractor
from src.application.use_cases.ingest_structured import IngestStructuredDocumentInteractor
from src.application.use_cases.query_assistant import QueryAssistantInteractor
from src.infrastructure.adapters.in_memory_signal_store import InMemorySignalStoreAdapter
from src.infrastructure.adapters.openai_assistant import OpenAIAssistantAdapter
from src.infrastructure.adapters.pgvector_store import PgVectorStoreAdapter
from src.infrastructure.config.settings import get_settings
from src.infrastructure.langchain.agents.react_agent import build_react_agent
from src.infrastructure.langchain.splitters.text_splitter import LangChainTextSplitterAdapter
from src.infrastructure.langchain.tools.search_tool import build_document_search_tool
from src.infrastructure.langchain.retrievers.vector_retriever import build_retriever


@lru_cache(maxsize=1)
def _vector_store() -> PgVectorStoreAdapter:
    settings = get_settings()
    return PgVectorStoreAdapter(
        database_url=settings.database_url,
        embedding_model=settings.embedding_model,
        openai_api_key=settings.openai_api_key.get_secret_value(),
    )


@lru_cache(maxsize=1)
def _ai_assistant() -> OpenAIAssistantAdapter:
    settings = get_settings()
    return OpenAIAssistantAdapter(
        api_key=settings.openai_api_key.get_secret_value(),
        model=settings.llm_model,
    )


@lru_cache(maxsize=1)
def _splitter() -> LangChainTextSplitterAdapter:
    return LangChainTextSplitterAdapter(chunk_size=800, chunk_overlap=100)


@lru_cache(maxsize=1)
def _signal_store() -> InMemorySignalStoreAdapter:
    return InMemorySignalStoreAdapter(max_size=1000)


# NOTE: HttpxScraperAdapter is available via
#   from src.infrastructure.adapters.httpx_scraper import HttpxScraperAdapter
# Wire it here when a use-case that needs web scraping is added.


# ── Public factory functions (used as FastAPI Depends) ────────────────────────

def get_ingest_structured_use_case() -> IngestStructuredDocumentInteractor:
    return IngestStructuredDocumentInteractor(
        vector_store=_vector_store(),
        splitter=_splitter(),
    )


def get_ingest_freshness_use_case() -> IngestFreshnessSignalInteractor:
    return IngestFreshnessSignalInteractor(signal_store=_signal_store())


def get_query_assistant_use_case() -> QueryAssistantInteractor:
    return QueryAssistantInteractor(
        vector_store=_vector_store(),
        ai_assistant=_ai_assistant(),
    )


def get_react_agent():
    """Return a ReAct agent wired with document search and LLM tools.

    The agent can multi-step reason and use tools to search the knowledge base.
    This is used by the console interface for complex, multi-step queries.
    """
    settings = get_settings()

    # Create a fresh LLM instance for the agent
    llm = ChatOpenAI(
        model=settings.llm_model,
        temperature=0.2,  # Slightly lower temp for more deterministic reasoning
        api_key=settings.openai_api_key.get_secret_value(),
        max_retries=3,
    )

    # Wire the document search tool to the vectorstore
    search_tool = build_document_search_tool(
        build_retriever(_vector_store()._store, k=4)
    )

    # Build the agent with tools
    return build_react_agent(
        tools=[search_tool],
        llm=llm,
        verbose=settings.debug,
    )


