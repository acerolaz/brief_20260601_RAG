"""LangSmith / custom tracing callbacks — cross-cutting infrastructure concern.

For basic LangSmith run tracing, only the env vars are needed:
    LANGCHAIN_TRACING_V2=true
    LANGSMITH_API_KEY=ls__...

This module provides additional custom callbacks for latency metrics and
sanitized logging (no prompt content is ever logged).
"""
from __future__ import annotations

import logging
import time
from typing import Any
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler

logger = logging.getLogger(__name__)


class LatencyLoggerCallback(BaseCallbackHandler):
    """Log LLM call latency and token counts — sanitized (no prompt content).

    Usage::

        from src.infrastructure.langchain.callbacks.tracing import LatencyLoggerCallback
        chain.invoke(input, config={"callbacks": [LatencyLoggerCallback()]})
    """

    def __init__(self) -> None:
        self._start_times: dict[UUID, float] = {}

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        self._start_times[run_id] = time.perf_counter()
        model = serialized.get("kwargs", {}).get("model_name", "unknown")
        logger.info("llm.start run_id=%s model=%s", run_id, model)

    def on_llm_end(self, response: Any, *, run_id: UUID, **kwargs: Any) -> None:
        elapsed = time.perf_counter() - self._start_times.pop(run_id, time.perf_counter())
        token_usage = (getattr(response, "llm_output", {}) or {}).get("token_usage", "n/a")
        logger.info("llm.end run_id=%s latency=%.3fs tokens=%s", run_id, elapsed, token_usage)

    def on_llm_error(self, error: Exception, *, run_id: UUID, **kwargs: Any) -> None:
        self._start_times.pop(run_id, None)
        logger.error("llm.error run_id=%s error=%r", run_id, error)

    def on_chain_start(
        self,
        serialized: dict[str, Any],
        inputs: dict[str, Any],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        name = serialized.get("id", ["unknown"])[-1]
        logger.debug("chain.start run_id=%s chain=%s", run_id, name)

    def on_chain_end(self, outputs: dict[str, Any], *, run_id: UUID, **kwargs: Any) -> None:
        logger.debug("chain.end run_id=%s", run_id)

