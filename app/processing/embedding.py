from app.client.ollama import OllamaClient
from app.config import settings


def embed_text(texts: list[str], client: OllamaClient) -> list[list[float]]:
    """Embed a list of texts, batching the calls to the embedding client.

    Note: batching stops a large document from becoming one unbounded request,
    and production would additionally want retries with backoff and a
    per-call timeout.
    """
    embeddings: list[list[float]] = []
    batch_size = settings.embed_batch_size

    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]
        batch_embeddings = client.embed(batch)

        for embedding in batch_embeddings:
            if len(embedding) != settings.embedding_dimensions:
                raise ValueError(
                    f"Expected {settings.embedding_dimensions}-dimensional embeddings, got {len(embedding)}"
                )

        embeddings.extend(batch_embeddings)

    return embeddings