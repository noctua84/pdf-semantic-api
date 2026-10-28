from uuid import UUID

from sqlalchemy import select

from app.db import session_scope
from app.models import Chunk, Document


def search(query_embedding: list[float], top_k: int, document_id: UUID | None = None):
    """
    Search for the chunks whose embeddings are closest to a query embedding.

    Note: plain columns are selected instead of the Chunk entity, so the returned rows
    hold scalars that stay readable after the session is committed and closed. Selecting
    the entity would hand back detached instances and keep the mapping to schemas,
    which belongs to the API layer, dependent on a live session.

    :param query_embedding: The embedding of the query to search for.
    :param top_k: The maximum number of chunks to return.
    :param document_id: Optional filter for a specific document id to search in.
    :return: Rows of (document_id, file_name, page_number, chunk_index, content, score).
    """
    distance = Chunk.embedding.cosine_distance(query_embedding)

    stmt = (
        select(
            Chunk.document_id,
            Document.file_name,
            Chunk.page_number,
            Chunk.chunk_index,
            Chunk.content,
            (1 - distance).label("score"),
        )
        .join(Document, Chunk.document_id == Document.id)
    )

    if document_id:
        stmt = stmt.where(Chunk.document_id == document_id)

    stmt = stmt.order_by(distance).limit(top_k)

    with session_scope() as db:
        return db.execute(stmt).all()
