"""Console driving adapter — interactive shell for the RAG system.

This is a driving adapter that exposes the application via a console interface.
Users can query the RAG assistant or use the AI agent for multi-step reasoning.
"""
from __future__ import annotations

import asyncio
import sys
from typing import Optional

from src.application.dtos import QueryRequest
from src.infrastructure.config.container import (
    get_query_assistant_use_case,
    get_react_agent,
)


class ConsoleInterface:
    """Interactive console interface for the RAG system.

    Supports two modes:
    1. **Query Mode**: Simple RAG question-answering (fast, deterministic).
    2. **Agent Mode**: ReAct agent with tool access (multi-step reasoning).
    """

    def __init__(self) -> None:
        self._query_use_case = get_query_assistant_use_case()
        self._agent = get_react_agent()

    async def run(self) -> None:
        """Start the interactive console."""
        self._print_banner()
        while True:
            try:
                await self._main_menu()
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                sys.exit(0)
            except EOFError:
                print("\n\n👋 Goodbye!\n")
                sys.exit(0)

    def _print_banner(self) -> None:
        """Print welcome banner."""
        banner = """
╔════════════════════════════════════════════════════════════════╗
║          🤖 Tech Watch RAG System — Interactive Console        ║
║                                                                ║
║  Query Mode:  Ask questions answered by the knowledge base    ║
║  Agent Mode:  Multi-step reasoning with tools                 ║
║                                                                ║
║  Commands: help | exit                                         ║
╚════════════════════════════════════════════════════════════════╝
"""
        print(banner)

    async def _main_menu(self) -> None:
        """Display main menu and handle user input."""
        print("\n📋 Main Menu:")
        print("  1) Query Mode (RAG search + answer)")
        print("  2) Agent Mode (multi-step reasoning)")
        print("  h) Help")
        print("  q) Quit")
        choice = input("\nChoose mode [1/2/h/q]: ").strip().lower()

        if choice == "1":
            await self._query_mode()
        elif choice == "2":
            await self._agent_mode()
        elif choice == "h":
            self._print_help()
        elif choice == "q":
            raise KeyboardInterrupt

    async def _query_mode(self) -> None:
        """RAG query mode — simple question-answering."""
        print("\n🔍 Query Mode")
        print("   (Type 'back' to return to main menu)\n")

        while True:
            question = input("❓ Question: ").strip()

            if question.lower() == "back":
                break
            if not question:
                print("   ⚠️  Please enter a question.")
                continue

            try:
                print("\n   ⏳ Searching knowledge base...\n")
                response = await self._query_use_case.execute(
                    QueryRequest(question=question, top_k=4)
                )

                print(f"   💡 Answer:")
                print(f"   {response.answer}\n")

                if response.source_ids:
                    print(f"   📚 Sources: {', '.join(response.source_ids)}\n")
            except Exception as e:
                print(f"   ❌ Error: {e}\n")

    async def _agent_mode(self) -> None:
        """Agent mode — multi-step reasoning with tools."""
        print("\n🤖 Agent Mode")
        print("   (Type 'back' to return to main menu)\n")
        print("   ⚠️  The agent can take multiple steps to answer complex questions.")
        print("   It may use tools to search documents, browse URLs, and reason.\n")

        while True:
            question = input("❓ Complex Question: ").strip()

            if question.lower() == "back":
                break
            if not question:
                print("   ⚠️  Please enter a question.")
                continue

            try:
                print("\n   ⏳ Agent is thinking...\n")
                # Agent execute returns a result dict with 'output' key
                result = await self._agent.ainvoke(
                    {"input": question},
                    config={"max_iterations": 10},
                )

                answer = result.get("output", "No answer generated.")
                print(f"   🎯 Agent Response:")
                print(f"   {answer}\n")
            except Exception as e:
                print(f"   ❌ Error: {e}\n")

    def _print_help(self) -> None:
        """Print help information."""
        help_text = """
📖 Help — Console Modes

1️⃣  QUERY MODE (Recommended for quick answers)
   • Fast, deterministic RAG search
   • Retrieves relevant documents from the knowledge base
   • Returns a single grounded answer
   • Best for: "What is X?" or "How does Y work?"

2️⃣  AGENT MODE (For complex multi-step reasoning)
   • Multi-step planning and reasoning
   • Can use tools: document search, external lookup
   • May iterate through multiple steps
   • Best for: "Compare X and Y", "How would I implement Z?"

💡 Tips:
   • Be specific in your questions
   • Use complete sentences
   • For Agent Mode, complex questions work better
   • The agent will show its reasoning steps (verbose mode)

🔗 Commands:
   • 'back'    - Return to main menu
   • 'exit'    - Exit the program
   • Ctrl+C    - Interrupt current operation
"""
        print(help_text)


async def main() -> None:
    """Entry point for the console application."""
    console = ConsoleInterface()
    await console.run()


if __name__ == "__main__":
    asyncio.run(main())


