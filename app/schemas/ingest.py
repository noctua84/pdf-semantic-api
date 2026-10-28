from datetime import datetime
from uuid import UUID

from fastapi import UploadFile
from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    u_file: UploadFile = Field(..., description="The PDF file to ingest.")


class IngestResponse(BaseModel):
    document_id: UUID
    file_name: str
    page_count: int = Field(
        ...,
        ge=0,
        description="The number of pages in the PDF, including pages no text could be extracted from.",
    )
    chunk_count: int = Field(..., description="The number of chunks the document was split into", ge=0)
    created_at: datetime