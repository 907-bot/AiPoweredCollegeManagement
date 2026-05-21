"""Database configuration and session management."""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Create async engine
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    poolclass=NullPool if settings.environment == "testing" else None,
    pool_pre_ping=True,
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


# Redis client
redis_client: Redis = Redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)


async def get_redis() -> Redis:
    """Get Redis client."""
    return redis_client


# Health check functions
async def check_database() -> bool:
    """Check if database connection is healthy."""
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False


async def check_redis() -> bool:
    """Check if Redis connection is healthy."""
    try:
        return await redis_client.ping()
    except Exception:
        return False