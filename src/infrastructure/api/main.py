"""FastAPI application entry point."""
from __future__ import annotations

from fastapi import APIRouter, Depends, FastAPI, status

from src.application.dtos import QueryRequest
from src.application.use_cases.query_assistant import QueryAssistantInteractor
from src.infrastructure.api.controllers.freshness_ingestion import router as freshness_router
from src.infrastructure.api.controllers.structured_ingestion import router as structured_router
from src.infrastructure.api.schemas import QueryHTTPRequest, QueryHTTPResponse
from src.infrastructure.config.container import get_query_assistant_use_case
from src.infrastructure.config.settings import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.project_name,
    description="Retrieval-Augmented Generation (RAG) system with LangChain",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

api_router = APIRouter(prefix=settings.api_v1_str)
api_router.include_router(structured_router)
api_router.include_router(freshness_router)


@api_router.post(
    "/query",
    response_model=QueryHTTPResponse,
    status_code=status.HTTP_200_OK,
    tags=["Query"],
    summary="Ask a question answered by the RAG assistant.",
)
async def query(
    body: QueryHTTPRequest,
    use_case: QueryAssistantInteractor = Depends(get_query_assistant_use_case),
) -> QueryHTTPResponse:
    result = await use_case.execute(QueryRequest(**body.model_dump()))
    return QueryHTTPResponse(answer=result.answer, source_ids=result.source_ids)


app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health() -> dict:
    return {"status": "ok"}

