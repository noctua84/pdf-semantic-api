from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Both can be cast into functions, decorated with @lru_cache
engine = create_engine(settings.database_url, echo=False, pool_pre_ping=True)
session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    db = session()

    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()