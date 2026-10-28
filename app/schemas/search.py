from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        description="The query to search for",
        min_length=1,
        max_length=4000,
        examples=["Some example query"]
    )

    document_id: UUID | None = Field(
        None,
        description="Optional filter for a specific document id to search in",
    )

    top_k: int = Field(
        default=5,
        description="The number of chunks to return",
        ge=1,
        le=25,
    )

    generate_answer: bool = Field(
        default=True,
        description="Whether to generate an answer to the query",
    )

    temperature: Annotated[float, Field(ge=0, le=1)] | None = Field(
        default=None,
        description="Sampling temperature for answer generation. Omit to use the configured TEMPERATURE setting.",
    )


class SearchMatch(BaseModel):
    document_id: UUID
    file_name: str
    page: int | None = Field(default=None, description="1-based page number the chunk came from.")
    chunk_index: int = Field(ge=0)
    text: str
    score: float = Field(
        ge=-1,
        le=1,
        description="Cosine similarity between the query and this chunk; 1 is identical.",
    )


class SearchResponse(BaseModel):
    matches: list[SearchMatch]
    answer: str | None = None