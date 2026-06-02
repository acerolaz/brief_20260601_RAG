"""Freshness signal ingestion HTTP controller."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status

from src.application.dtos import IngestFreshnessSignalRequest
from src.application.use_cases.ingest_freshness import IngestFreshnessSignalInteractor
from src.infrastructure.api.schemas import IngestSignalHTTPRequest, IngestSignalHTTPResponse
from src.infrastructure.config.container import get_ingest_freshness_use_case

router = APIRouter(prefix="/ingest/freshness", tags=["Freshness Ingestion"])


@router.post(
    "/",
    response_model=IngestSignalHTTPResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest a freshness signal (webhook / RSS entry).",
)
async def ingest_freshness_signal(
    body: IngestSignalHTTPRequest,
    use_case: IngestFreshnessSignalInteractor = Depends(get_ingest_freshness_use_case),
) -> IngestSignalHTTPResponse:
    request = IngestFreshnessSignalRequest(**body.model_dump())
    result = await use_case.execute(request)
    return IngestSignalHTTPResponse(
        signal_id=result.signal_id,
        acknowledged=result.acknowledged,
    )

