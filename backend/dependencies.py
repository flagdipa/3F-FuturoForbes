from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .config import settings

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from sqlmodel import Session as SQLModelSession

def get_db() -> Generator[SQLModelSession, None, None]:
    with SQLModelSession(engine) as session:
        yield session

# Add auth dependencies here later
# def get_current_user(...)
