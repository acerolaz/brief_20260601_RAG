"""Summarization LCEL chain — infrastructure adapter."""
from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from prompts.loader import load_prompt


def build_summary_chain(llm: ChatOpenAI):
    """Build and return the summarization LCEL chain.

    Chain signature: ``{"text": str}`` → ``str``

    Args:
        llm: Initialised chat model.

    Returns:
        A composed ``Runnable[dict, str]``.
    """
    system_prompt = load_prompt("summary_system.txt")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
        ]
    )
    return prompt | llm | StrOutputParser()

