"""ReAct agent adapter — infrastructure adapter layer.

Use agents when dynamic tool selection is required (e.g. multi-step reasoning).
For deterministic pipelines, prefer chains (``src/infrastructure/langchain/chains/``).
"""
from __future__ import annotations

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

_REACT_TEMPLATE = """Answer the following question as best you can using the available tools.

Tools: {tools}

Use the following format:
Thought: think about what to do
Action: the action to take, one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Observation as needed)
Thought: I now know the final answer
Final Answer: the final answer to the original question

Question: {input}
{agent_scratchpad}"""


def build_react_agent(
    tools: list[BaseTool],
    llm: ChatOpenAI,
    verbose: bool = False,
) -> AgentExecutor:
    """Build a ReAct AgentExecutor with the provided tools.

    Args:
        tools: List of typed tool adapters (from ``src/infrastructure/langchain/tools/``).
        llm: Initialised chat model; bind tools externally if needed.
        verbose: Log agent reasoning steps (disable in production).

    Returns:
        An :class:`~langchain.agents.AgentExecutor` ready to ``invoke`` or ``ainvoke``.
    """
    prompt = PromptTemplate.from_template(_REACT_TEMPLATE)
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        handle_parsing_errors=True,
        max_iterations=10,
    )

