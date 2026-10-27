from app.client.ollama import OllamaClient


def embed_text(texts: list[str], client: OllamaClient):
    embeddings = client.embed(texts)

    if embeddings and len(embeddings[0]) != 1024:
        raise ValueError(f"Expected 1024-dimensional embeddings, got {len(embeddings[0])}")

    return embeddings