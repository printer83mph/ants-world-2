from collections.abc import Generator
from typing import Callable

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


def create_database_engine(database_url: str):
    """Create SQLAlchemy engine with appropriate settings"""
    if database_url.startswith("sqlite"):
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
    else:
        # For PostgreSQL and other databases
        engine = create_engine(database_url)
    return engine


def create_session_local(engine: Engine) -> sessionmaker[Session]:
    """Create SessionLocal class for database sessions"""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_database_dependency(
    SessionLocal: sessionmaker[Session],
) -> Callable[[], Generator[Session, None, None]]:
    """Create database dependency function"""

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    return get_db
