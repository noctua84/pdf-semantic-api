from fastapi import FastAPI

from app.client.ollama import OllamaClient
from app.config import settings




def create_app() -> FastAPI:
    f_app = FastAPI(
        title=settings.app_name,
    )

    """
    In a production ready app, you'd have health and metrics endpoints as well as error handling middleware.
    """

    return f_app


app = create_app()
