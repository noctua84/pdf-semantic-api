from sqlalchemy import text

from app.db import engine
from app.models import Base


def init_db() -> None:
    """
    Initialize the database.

    Note: for production, I would use Alembic to manage database migrations.
    This is for PoC simplicity.
    """

    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    Base.metadata.create_all(bind=engine)