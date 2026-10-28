from uuid import uuid4

from app.db import session_scope
from app.models import Document, Chunk
from app.processing.dto import ExtractedChunk, SavedDocument


def save_data(file_name: str, page_count: int, chunks: list[ExtractedChunk], embeddings: list[list[float]]) -> SavedDocument:
    """
    Persist a document and its embedded chunks in a single transaction.

    Note: a SavedDocument DTO is returned instead of the Document entity, so no ORM
    instance escapes the session scope. The committed instance would be expired and
    detached once the scope closes, which makes reading attributes such as the
    server-generated created_at raise.

    :param file_name: The name of the ingested file.
    :param page_count: The number of pages the file contained.
    :param chunks: The chunks extracted from the file.
    :param embeddings: The embeddings of the chunks, in the same order as chunks.
    :return: SavedDocument holding the persisted document data.
    """
    doc = Document(
        id=uuid4(),
        file_name=file_name,
        page_count=page_count,
        chunk_count=len(chunks)
    )

    chunk_list = [
        Chunk(
            document_id=doc.id,
            page_number=chunk.page_number,
            chunk_index=chunk.chunk_index,
            embedding=embedding,
            content=chunk.text
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]

    with session_scope() as db:
        db.add(doc)
        db.add_all(chunk_list)
        db.flush()
        db.refresh(doc)

        return SavedDocument(
            id=doc.id,
            file_name=doc.file_name,
            page_count=doc.page_count,
            chunk_count=doc.chunk_count,
            created_at=doc.created_at
        )
