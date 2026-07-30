"""Database setup and shared ORM infrastructure for Fragile."""

from datetime import datetime
from pathlib import Path

from sqlalchemy import DateTime, Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from tomorrow.conf import settings
from tomorrow.models.constants import CheckpointType


class Base(DeclarativeBase):
    """Base class for Fragile ORM models."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )


def get_engine() -> Engine:
    """Return the shared database engine for the configured database path."""
    path = Path(settings.CHECKPOINT[CheckpointType.SQLITE]["path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{path}")


def get_async_engine() -> AsyncEngine:
    """Return the shared asynchronous database engine for the configured path."""
    path = Path(settings.CHECKPOINT[CheckpointType.SQLITE]["path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    return create_async_engine(f"sqlite+aiosqlite:///{path}")


def get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return a factory for asynchronous ORM sessions."""
    return async_sessionmaker(get_async_engine(), expire_on_commit=False)


async def create_tables_async(async_engine: AsyncEngine) -> None:
    """Create Fragile tables using an asynchronous engine."""
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def get_initialized_async_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return an asynchronous session factory after initializing Fragile tables."""
    async_engine = get_async_engine()
    await create_tables_async(async_engine)
    return async_sessionmaker(async_engine, expire_on_commit=False)


engine = get_engine()
Base.metadata.create_all(engine)
