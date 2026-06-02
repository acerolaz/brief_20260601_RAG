"""Prompt template loader.

All canonical prompts are stored as plain-text files in this directory.
Load them via :func:`load_prompt` to keep prompt logic decoupled from Python code.
"""
from __future__ import annotations

from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent


def load_prompt(filename: str) -> str:
    """Load a prompt template from the ``prompts/`` directory.

    Args:
        filename: File name relative to the ``prompts/`` directory (e.g. ``"rag_system.txt"``).

    Returns:
        The raw prompt string ready for use with :class:`~langchain_core.prompts.ChatPromptTemplate`.

    Raises:
        FileNotFoundError: If the prompt file does not exist.
    """
    path = _PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8").strip()

