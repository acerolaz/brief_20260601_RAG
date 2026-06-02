"""OpenAI assistant adapter — implements AIAssistantPort using LangChain LCEL.

For full retrieval-augmented chains composed with a retriever, use
``src/infrastructure/langchain/chains/rag_chain.build_rag_chain`` directly.
"""
from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from prompts.loader import load_prompt
from src.domain.exceptions import AIAssistantError


class OpenAIAssistantAdapter:
    """Driven adapter: generates answers via OpenAI chat model (LCEL chain).

    Uses the canonical RAG prompt from ``prompts/rag_system.txt``.
    For retrieval-augmented chains composed with a live retriever, use
    ``src/infrastructure/langchain/chains/rag_chain.build_rag_chain`` directly.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o", temperature: float = 0.0) -> None:
        system_prompt = load_prompt("rag_system.txt")
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{question}"),
            ]
        )
        llm = ChatOpenAI(model=model, temperature=temperature, api_key=api_key, max_retries=3)
        self._chain = prompt | llm | StrOutputParser()

    async def answer(self, question: str, context: str) -> str:
        """Generate an answer grounded in *context*."""
        try:
            return await self._chain.ainvoke({"context": context, "question": question})
        except Exception as exc:
            raise AIAssistantError(f"LLM call failed: {exc}") from exc


