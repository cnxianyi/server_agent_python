"""SQLAlchemy 2.x async database setup."""

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import Settings


def _async_database_url(database_url: str) -> str:
    """Ensure a plain PostgreSQL URL uses SQLAlchemy's asyncpg dialect."""

    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    return database_url


def create_engine(settings: Settings) -> AsyncEngine:
    """Create the shared SQLAlchemy async engine."""

    return create_async_engine(
        _async_database_url(settings.database_url),
        pool_size=settings.db_pool_min_size,
        max_overflow=max(0, settings.db_pool_max_size - settings.db_pool_min_size),
        pool_timeout=settings.db_connect_timeout,
        pool_pre_ping=True,
        connect_args={"timeout": settings.db_connect_timeout},
    )


def create_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create the SQLAlchemy 2.x async session factory."""

    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that provides one session per request."""

    session_factory: async_sessionmaker[AsyncSession] = (
        request.app.state.session_factory
    )
    async with session_factory() as session:
        yield session


async def ping(engine: AsyncEngine) -> None:
    """Run a minimal SQLAlchemy Core query to verify PostgreSQL connectivity."""

    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
