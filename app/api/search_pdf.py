from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.client.ollama import OllamaClient, get_ollama_client
from app.processing.embedding import embed_text
from app.processing.search import search
from app.schemas import SearchResponse, ErrorResponse, SearchRequest, SearchMatch

router = APIRouter()

@router.post(
    "/search_pdf",
    response_model=SearchResponse,
    responses={
        200: {"model": SearchResponse},
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
def search_pdf(request: SearchRequest, client: Annotated[OllamaClient, Depends(get_ollama_client)]):
    """
    Search for PDF documents based on a query using an Ollama client.

    :param request: The search request containing the query text.
    :param client: The Ollama client used for embedding the query text.
    :return: The search response containing the search results.
    """
    # 1. Embed the query text using the provided Ollama client
    try:
        query_embedding = embed_text([request.query], client)[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 2. Retrieve from DB
    results = search(
        query_embedding=query_embedding,
        top_k=request.top_k,
        document_id=request.document_id,
    )

    # 3. Mapping
    matches = []
    context_texts = []

    for row in results:
        matches.append(SearchMatch(
            document_id=row.document_id,
            file_name=row.file_name,
            page=row.page_number,
            chunk_index=row.chunk_index,
            text=row.content,
            score=float(row.score),
        ))
        context_texts.append(row.content)

    # 4. generate Answer
    answer = None
    if request.generate_answer and matches:
        full_context = "\n\n---\n\n".join(context_texts)
        prompt = f"Context:\n{full_context}\n\nQuestion: {request.query}"

        try:
            answer = client.chat(prompt, temperature=request.temperature)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Error generating answer: {str(e)}")

    return SearchResponse(
        answer=answer,
        matches=matches
    )
