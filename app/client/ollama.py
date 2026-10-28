from functools import lru_cache

import httpx

from app.config import settings


system_prompt = (
    "You are a helpful assistant. Answer the user's question using "
    "ONLY the provided document context. If the answer is not in the "
    "context, state that you do not know. Do not use outside knowledge and do not make things up."
)

class OllamaClient:
    def __init__(self, base_url: str, embed_model: str, chat_model: str):
        self.base_url = base_url
        self.embed_model = embed_model
        self.chat_model = chat_model
        self.client = httpx.Client(base_url=base_url, timeout=600)
        self.async_client = httpx.AsyncClient(base_url=base_url, timeout=600)

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.post(
            "/api/embed",
            json={
                "model": self.embed_model,
                "input": texts,
            },
        )
        response.raise_for_status()
        return response.json()["embeddings"]

    def chat(self, prompt: str, temperature: float | None = None) -> str:
        response = self.client.post(
            "/api/chat",
            json={
                "model": self.chat_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                # We only read message.content, so reasoning tokens would be generated and discarded.
                # On a small context window, they can consume it entirely, leaving an empty answer.
                "think": False,
                "options": {
                    "temperature": settings.temperature if temperature is None else temperature
                }
            },
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    async def async_embed(self, texts: list[str]) -> list[list[float]]:
        response = await self.async_client.post(
            "/api/embed",
            json={
                "model": self.embed_model,
                "input": texts,
            },
        )
        response.raise_for_status()
        return response.json()["embeddings"]

    async def async_chat(self, prompt: str, temperature: float | None = None) -> str:
        response = await self.async_client.post(
            "/api/chat",
            json={
                "model": self.chat_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "think": False,
                "options": {
                    "temperature": settings.temperature if temperature is None else temperature
                }
            },
        )
        response.raise_for_status()
        return response.json()["message"]["content"]


@lru_cache
def get_ollama_client() -> OllamaClient:
    return OllamaClient(
        base_url=settings.ollama_base_url,
        embed_model=settings.ollama_embed_model,
        chat_model=settings.ollama_chat_model,
    )