from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.pool import QueuePool
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Configure connection pooling for better performance
pool_config = {
    "poolclass": QueuePool,
    "pool_size": 20,  # Max simultaneous connections
    "max_overflow": 10,  # Extra connections during spikes
    "pool_timeout": 30,  # Timeout waiting for connection (seconds)
    "pool_recycle": 3600,  # Recycle connections after 1 hour
    "pool_pre_ping": True,  # Verify connections before using
}

# Check if using SQLite (no pooling needed for single-file DB)
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite doesn't benefit from connection pooling
    engine = create_engine(settings.DATABASE_URL, echo=False)
    logger.info("Database configured: SQLite (no pooling)")
else:
    # PostgreSQL/MySQL benefit from pooling
    engine = create_engine(
        settings.DATABASE_URL,
        echo=False,
        **pool_config
    )
    logger.info(f"Database configured with connection pooling (size=20, overflow=10)")

def init_db() -> None:
    """
    Initialize the database by creating all tables defined in SQLModel metadata.
    This should be called during application startup.
    """
    SQLModel.metadata.create_all(engine)

from typing import Generator

def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a new database session for each request.
    Automatically closes the session after the request is finished.
    
    Yields:
        A SQLModel Session instance.
    """
    with Session(engine) as session:
        yield session
