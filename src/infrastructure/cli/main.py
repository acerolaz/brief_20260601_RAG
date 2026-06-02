"""CLI entry point — routes to console or direct query."""
from __future__ import annotations

import asyncio
import sys


def main() -> None:
    """Main CLI entry point.

    Usage:
        # Interactive console (default)
        python -m src.infrastructure.cli.main

        # Direct query
        python -m src.infrastructure.cli.main "Your question here"
    """
    if len(sys.argv) > 1:
        # Direct query mode
        question = " ".join(sys.argv[1:])
        asyncio.run(_direct_query(question))
    else:
        # Interactive console mode
        from src.infrastructure.console import ConsoleInterface

        console = ConsoleInterface()
        asyncio.run(console.run())


async def _direct_query(question: str) -> None:
    """Execute a single query and exit."""
    from src.infrastructure.config.container import get_query_assistant_use_case
    from src.application.dtos import QueryRequest

    try:
        use_case = get_query_assistant_use_case()
        response = await use_case.execute(QueryRequest(question=question))
        print("\n💡 Answer:")
        print(response.answer)
        if response.source_ids:
            print(f"\n📚 Sources: {', '.join(response.source_ids)}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

