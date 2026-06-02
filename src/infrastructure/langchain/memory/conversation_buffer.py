"""Conversation memory adapter — infrastructure adapter layer.

Design: stateless by default. Memory is opt-in and stores minimal context.
Document retention and erasure policies must be defined if PII may be present.
For production, replace the in-process buffer with a DB-backed store.
"""
from __future__ import annotations

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class ConversationBuffer:
    """Lightweight in-process conversation buffer (not persistent).

    - Not threadsafe: use one instance per request context in async servers.
    - Call :meth:`clear` to erase user data on request (GDPR compliance).
    """

    def __init__(self, max_turns: int = 10) -> None:
        self._history: list[BaseMessage] = []
        self.max_turns = max_turns

    # ── Write ──────────────────────────────────────────────────────────────────

    def add_user_message(self, content: str) -> None:
        self._history.append(HumanMessage(content=content))
        self._trim()

    def add_ai_message(self, content: str) -> None:
        self._history.append(AIMessage(content=content))
        self._trim()

    # ── Read ───────────────────────────────────────────────────────────────────

    def get_history(self) -> list[BaseMessage]:
        """Return a copy of the current conversation history."""
        return list(self._history)

    # ── Erasure ────────────────────────────────────────────────────────────────

    def clear(self) -> None:
        """Erase all stored messages (user data erasure / GDPR)."""
        self._history.clear()

    # ── Internal ───────────────────────────────────────────────────────────────

    def _trim(self) -> None:
        """Keep only the most recent *max_turns* message pairs."""
        max_messages = self.max_turns * 2
        if len(self._history) > max_messages:
            self._history = self._history[-max_messages:]

