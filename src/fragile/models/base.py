"""Database setup and shared ORM infrastructure for Fragile."""

from datetime import datetime
from pathlib import Path

from sqlalchemy import DateTime
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


def get_engine() -> AsyncEngine:
    """Return the shared asynchronous database engine for the configured path."""
    path = Path(settings.CHECKPOINT[CheckpointType.SQLITE]["path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    return create_async_engine(f"sqlite+aiosqlite:///{path}")


async def create_tables(async_engine: AsyncEngine) -> None:
    """Create Fragile tables using an asynchronous engine."""
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def get_initialized_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return an asynchronous session factory after initializing Fragile tables."""
    await create_tables(engine)
    return async_sessionmaker(engine, expire_on_commit=False)


engine = get_engine()
