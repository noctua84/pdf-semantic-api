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

    temperature: float = Field(
        default=0.7,
        description="The temperature to use for the answer generation",
        ge=0,
        le=1,
    )


class SearchMatch(BaseModel):
    document_id: UUID
    file_name: str
    page: int | None = None
    chunk_index: int = Field(ge=0)
    text: str
    score: float = Field(ge=0, le=1)


class SearchResponse(BaseModel):
    matches: list[SearchMatch]
    answer: str | None = None