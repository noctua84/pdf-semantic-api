from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ExtractedPage:
    page_number: int
    text: str


@dataclass(frozen=True, slots=True)
class ExtractedDocument:
    page_count: int
    pages: list[ExtractedPage]


@dataclass(frozen=True, slots=True)
class ExtractedChunk:
    page_number: int
    chunk_index: int
    text: str


@dataclass(frozen=True, slots=True)
class SavedDocument:
    id: UUID
    file_name: str
    page_count: int
    chunk_count: int
    created_at: datetime
