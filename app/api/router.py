from fastapi import APIRouter, Depends

from app.client.ollama import OllamaClient
from app.config import settings

ollama_client = OllamaClient(
    base_url=settings.ollama_base_url,
    embed_model=settings.ollama_embed_model,
    chat_model=settings.ollama_chat_model,
)

router = APIRouter()