from fastapi import FastAPI

from app.config import settings
from app.api.router import router as api_router


def create_app() -> FastAPI:
    f_app = FastAPI(
        title=settings.app_name,
    )

    """
    In a production ready app, you'd have health and metrics endpoints as well as error handling middleware.
    """

    f_app.include_router(api_router)

    return f_app


app = create_app()
