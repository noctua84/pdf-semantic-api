from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.client.ollama import OllamaClient
from app.config import settings
from app.processing.chunking import chunk_pages
from app.processing.embedding import embed_text
from app.processing.pdf import extract_pdf_pages
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
def ingest_pdf(client: OllamaClient, u_file: UploadFile = File(...)):
    chunk_size = settings.chunk_size
    chunk_overlap = settings.chunk_overlap

    if not u_file.filename or not u_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file format. Only PDF files are supported.")

    pdf_bytes = u_file.file.read()

    if not pdf_bytes:
        raise HTTPException(status_code=422, detail="Uploaded file is empty.")

    pages = extract_pdf_pages(pdf_bytes)

    if not pages:
        raise HTTPException(status_code=422, detail="No extractable text found. The PDF may be scanned of image-only")

    chunks = chunk_pages(pages, chunk_size, chunk_overlap)

    if not chunks:
        raise HTTPException(status_code=422, detail="No usable text chunks could be extracted from the PDF.")

    texts = [chunk.text for chunk in chunks]

    try:
        embeddings = embed_text(texts, client=client)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error embedding text: {str(e)}")

    if len(embeddings) != len(chunks):
        raise HTTPException(status_code=500, detail="Number of embeddings does not match chunks.")

    document_id = uuid4()