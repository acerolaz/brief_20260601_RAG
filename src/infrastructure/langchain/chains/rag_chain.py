"""RAG LCEL chain — infrastructure adapter.

This chain is used by OpenAIAssistantAdapter to answer questions grounded in context.
It can also be used standalone for testing or alternative entry points.
"""
from __future__ import annotations

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI

from prompts.loader import load_prompt


def _format_docs(docs: list[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain(
    retriever: BaseRetriever,
    llm: ChatOpenAI,
):
    """Build and return the RAG LCEL chain.

    Chain signature: ``str`` → ``str``

    Pipeline:
        retriever → format_docs → prompt → llm → str

    Args:
        retriever: Any LangChain ``BaseRetriever`` (wraps vectorstore).
        llm: Initialised chat model.

    Returns:
        A composed ``Runnable[str, str]``.
    """
    system_prompt = load_prompt("rag_system.txt")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{question}"),
        ]
    )

    return (
        {
            "context": retriever | RunnableLambda(_format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

