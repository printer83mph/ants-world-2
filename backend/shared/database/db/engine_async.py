from collections.abc import AsyncGenerator
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine as sa_create_async_engine


def create_async_engine(database_url: str) -> AsyncEngine:
    """Create SQLAlchemy async engine with appropriate settings"""
    return sa_create_async_engine(database_url)


def create_async_session(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create SessionLocal class for database sessions"""
    return async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_database_dependency(
    AsyncSessionLocal: async_sessionmaker[AsyncSession],
) -> Callable[[], AsyncGenerator[AsyncSession, None]]:
    """Create database dependency function"""

    async def get_db():
        async with AsyncSessionLocal() as session:
            yield session

    return get_db
