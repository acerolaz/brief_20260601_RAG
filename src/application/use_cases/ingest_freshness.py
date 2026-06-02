"""Use case: ingest a freshness signal (webhook / RSS entry).

High-frequency events are validated, converted to domain entities, and persisted
via the SignalStorePort. Downstream consumers (cache invalidation, trending topics)
read from the store asynchronously.
"""
from __future__ import annotations

from src.application.dtos import IngestFreshnessSignalRequest, IngestFreshnessSignalResponse
from src.application.ports.outbound import SignalStorePort
from src.domain.entities import Signal, SignalType


class IngestFreshnessSignalInteractor:
    """Validate, build domain entity, and persist a freshness signal."""

    def __init__(self, signal_store: SignalStorePort) -> None:
        self._signal_store = signal_store

    async def execute(
        self, request: IngestFreshnessSignalRequest
    ) -> IngestFreshnessSignalResponse:
        try:
            signal_type = SignalType(request.signal_type)
        except ValueError:
            return IngestFreshnessSignalResponse(
                signal_id=request.signal_id, acknowledged=False
            )

        signal = Signal(
            id=request.signal_id,
            signal_type=signal_type,
            topic=request.topic,
            payload=request.payload,
        )
        await self._signal_store.save(signal)
        return IngestFreshnessSignalResponse(signal_id=request.signal_id, acknowledged=True)
