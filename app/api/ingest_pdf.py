from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Depends

from app.client.ollama import OllamaClient, get_ollama_client
from app.config import settings
from app.processing.chunking import chunk_pages
from app.processing.embedding import embed_text
from app.processing.pdf import extract_pdf_pages
from app.processing.save_data import save_data
from app.schemas.error import ErrorResponse
from app.schemas.ingest import IngestRequest, IngestResponse

router = APIRouter()


@router.post(
    "/ingest_pdf",
    response_model=IngestResponse,
    responses={
        200: {"model": IngestResponse},
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def ingest_pdf(
    client: Annotated[OllamaClient, Depends(get_ollama_client)],
    request: Annotated[IngestRequest, Form(media_type="multipart/form-data")],
):
    """
    Ingest a PDF file and process its content.

    Note: for simplicity, the route handler only has simple validation and no logging.
    For production, adding meaningful logging would be necessary and also considering
    modularization to not overload the handler with concerns it should not carry.
    Maybe even OpenTelemetry and/or LangFuse.

    :param client: Ollama client instance.
    :param request: Multipart form data containing the PDF file to ingest.
    :return: IngestResponse object.
    """
    u_file = request.u_file
    chunk_size = settings.chunk_size
    chunk_overlap = settings.chunk_overlap

    # 1. Verify file type
    if not u_file.filename or not u_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file format. Only PDF files are supported.")

    # 2. Extract text
    try:
        pdf_bytes = u_file.file.read()
        extracted = extract_pdf_pages(pdf_bytes)
        pages = extracted.pages
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error reading uploaded file: {str(e)}")

    if not pages:
        raise HTTPException(status_code=422, detail="No extractable text found. The PDF may be scanned of image-only")

    # 3. Chunk text
    chunks = chunk_pages(pages, chunk_size, chunk_overlap)

    if not chunks:
        raise HTTPException(status_code=422, detail="No usable text chunks could be extracted from the PDF.")

    # 4. Get embeddings
    try:
        texts = [chunk.text for chunk in chunks]
        embeddings = embed_text(texts, client=client)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error embedding text: {str(e)}")

    if len(embeddings) != len(chunks):
        raise HTTPException(status_code=500, detail="Number of embeddings does not match chunks.")

    # 5. Save the extracted and embedded data
    try:
        saved = save_data(u_file.filename, extracted.page_count, chunks, embeddings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving data: {str(e)}")

    # 6. Return response
    return IngestResponse(
        document_id=saved.id,
        file_name=saved.file_name,
        page_count=saved.page_count,
        chunk_count=saved.chunk_count,
        created_at=saved.created_at
    )
