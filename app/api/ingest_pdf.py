from fastapi import APIRouter

from app.client.ollama import OllamaClient
from app.config import settings
from app.shemas.error import ErrorResponse
from app.shemas.ingest import IngestResponse

router = APIRouter()


@router.post(
    "/ingest_pdf",
    response_model=IngestResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def ingest_pdf(client: OllamaClient):
    chunk_size = settings.chunk_size
    chunk_overlap = settings.chunk_overlap