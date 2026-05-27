"""Database configuration and session management."""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings


def _fix_db_url(url: str) -> str:
    """Convert any postgres URL variant to the asyncpg-compatible format."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


# Create async engine — lazy connection, no actual DB call here
engine: AsyncEngine = create_async_engine(
    _fix_db_url(settings.database_url),
    echo=settings.debug,
    pool_pre_ping=True,
    # pool_size/max_overflow only apply when NOT using NullPool
    **({} if settings.environment == "testing" else {
        "pool_size": settings.database_pool_size,
        "max_overflow": settings.database_max_overflow,
    }),
    poolclass=NullPool if settings.environment == "testing" else None,
)

# Async session factory
async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions."""
    async with get_db_session() as session:
        yield session


# Redis client — lazy connection, no actual call here
redis_client: Redis = Redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)


async def get_redis() -> Redis:
    """Get Redis client."""
    return redis_client
