from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    document_id: UUID
    filename: str
    page_count: int = Field(..., ge=0)
    chunk_count: int = Field(..., description="The number of chunks the document was split into", ge=0)
    created_at: datetime