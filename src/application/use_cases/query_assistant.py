"""Use case: answer a user question using the RAG assistant.

Retrieves the most relevant chunks from the vector store, formats them as context,
then delegates answer generation to the AI assistant port.
"""
from __future__ import annotations

from src.application.dtos import QueryRequest, QueryResponse
from src.application.ports.outbound import AIAssistantPort, VectorStorePort


class QueryAssistantInteractor:
    """RAG query pipeline: retrieve chunks → build context → generate answer."""

    def __init__(self, vector_store: VectorStorePort, ai_assistant: AIAssistantPort) -> None:
        self._vector_store = vector_store
        self._ai_assistant = ai_assistant

    async def execute(self, request: QueryRequest) -> QueryResponse:
        chunks = await self._vector_store.similarity_search(
            query=request.question,
            top_k=request.top_k,
        )

        if not chunks:
            return QueryResponse(
                answer="I don't have enough information to answer that.",
                source_ids=[],
            )

        context = "\n\n".join(chunk.text for chunk in chunks)
        answer = await self._ai_assistant.answer(
            question=request.question,
            context=context,
        )

        return QueryResponse(
            answer=answer,
            source_ids=list({chunk.source_id for chunk in chunks}),
        )

