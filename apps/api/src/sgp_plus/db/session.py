"""Database session management"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sgp_plus.core.config import settings
from sgp_plus.db.base import Base

engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database (create tables)"""
    Base.metadata.create_all(bind=engine)
