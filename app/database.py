"""
Database connection setup (PostgreSQL via SQLAlchemy, async engine).

Connection string is read from the DATABASE_URL environment variable so it
can be overridden in docker-compose / k8s / .env without touching code.
"""
import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/mtm_db",
)

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


async def get_db():
    """FastAPI dependency that yields an async DB session and closes it afterwards."""
    async with AsyncSessionLocal() as session:
        yield session
