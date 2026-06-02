"""Structured ingestion HTTP controller."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status

from src.application.dtos import IngestDocumentRequest
from src.application.use_cases.ingest_structured import IngestStructuredDocumentInteractor
from src.infrastructure.api.schemas import IngestDocumentHTTPRequest, IngestDocumentHTTPResponse
from src.infrastructure.config.container import get_ingest_structured_use_case

router = APIRouter(prefix="/ingest/structured", tags=["Structured Ingestion"])


@router.post(
    "/",
    response_model=IngestDocumentHTTPResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a structured document (PDF, whitepaper) into the knowledge base.",
)
async def ingest_structured_document(
    body: IngestDocumentHTTPRequest,
    use_case: IngestStructuredDocumentInteractor = Depends(get_ingest_structured_use_case),
) -> IngestDocumentHTTPResponse:
    request = IngestDocumentRequest(**body.model_dump())
    result = await use_case.execute(request)
    return IngestDocumentHTTPResponse(
        document_id=result.document_id,
        chunks_stored=result.chunks_stored,
    )

