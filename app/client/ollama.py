import httpx


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
                "prompt": texts,
            },
        )
        response.raise_for_status()
        return response.json()["embeddings"]

    def chat(self, prompt: str) -> str:
        response = self.client.post(
            "/api/generate",
            json={
                "model": self.chat_model,

                "prompt": prompt,
            },
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    async def async_embed(self, texts: list[str]) -> list[list[float]]:
        response = await self.async_client.post(
            "/api/embed",
            json={
                "model": self.embed_model,
                "prompt": texts,
            },
        )
        response.raise_for_status()
        return response.json()["embeddings"]

    async def async_chat(self, prompt: str) -> str:
        response = await self.async_client.post(
            "/api/generate",
            json={
                "model": self.chat_model,
                "prompt": prompt,
            },
        )
        response.raise_for_status()
        return response.json()["message"]["content"]