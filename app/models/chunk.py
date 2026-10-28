from datetime import datetime
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, ForeignKey, Text, DateTime, func
from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.document import Document


class Chunk(Base):
    """
    Represents a chunk of text extracted from a document.

    Attributes:
        id (int): The unique identifier of the chunk.
        document_id (UUID): The unique identifier of the document associated with the chunk.
        page_number (int | None): The page number where the chunk is located.
        chunk_index (int): The index of the chunk within the document.
        content (str): The text content of the chunk.
        embedding (Vector): The embedding vector of the chunk.
        created_at (datetime): The timestamp when the chunk was created.
        document (Document): The document associated with the chunk.
    """
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector(settings.embedding_dimensions), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    document: Mapped["Document"] = relationship(back_populates="chunks")