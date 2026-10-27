from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExtractedPage:
    page_number: int
    text: str


@dataclass(frozen=True, slots=True)
class ExtractedChunk:
    page_number: int
    chunk_index: int
    text: str