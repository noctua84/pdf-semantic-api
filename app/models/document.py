from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, DateTime, Integer
from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models import Base
from app.models.chunk import Chunk


class Document(Base):
    """
    Represents a document in the database.

    Attributes:
        id (UUID): The unique identifier of the document.
        file_name (str): The name of the file associated with the document.
        page_count (int): The number of pages in the document.
        chunk_count (int): The number of chunks in the document.
        created_at (datetime): The timestamp when the document was created.
        chunks (list[Chunk]): The chunks associated with the document.
    """
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True),primary_key=True, default=uuid4)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())

    chunks: Mapped[list[Chunk]] = relationship(back_populates="document", cascade="all, delete-orphan")