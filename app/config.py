from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_PATH = Path(__file__).parent.parent

class Settings(BaseSettings):
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_embed_model: str = "qwen3-embedding:0.6b"
    ollama_chat_model: str
    embedding_dimensions: int = 1024 # embedding dimensions for qwen3 embedding models

    # App
    app_name: str = "pdf semantic search"
    log_level: str = "INFO"
    host: str = "localhost"
    port: int = 8000

    # Ingestion
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Database
    database_url: str


    model_config = SettingsConfigDict(env_file=_PROJECT_PATH/".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()