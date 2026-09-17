"""Database setup and shared ORM infrastructure for Fragile."""

from asyncio import Lock
from datetime import datetime
from pathlib import Path

from sqlalchemy import DateTime, inspect, text
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
        await connection.run_sync(_migrate_account_provider)
        await connection.run_sync(_migrate_account_model)
        await connection.run_sync(_migrate_session_output_thinking)
        await connection.run_sync(_migrate_session_output_trace)


def _migrate_account_provider(connection: object) -> None:
    """Add the provider column to databases created before account types existed."""
    inspector = inspect(connection)
    if "fragile_account" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("fragile_account")}
    if "provider" not in columns:
        connection.execute(
            text("ALTER TABLE fragile_account ADD COLUMN provider VARCHAR(32) NOT NULL DEFAULT 'anthropic'")
        )


def _migrate_account_model(connection: object) -> None:
    """Add the selected model column to legacy account databases."""
    inspector = inspect(connection)
    if "fragile_account" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("fragile_account")}
    if "model" not in columns:
        connection.execute(text("ALTER TABLE fragile_account ADD COLUMN model VARCHAR(256)"))


def _migrate_session_output_thinking(connection: object) -> None:
    """Add the thinking output column to legacy session output databases."""
    inspector = inspect(connection)
    if "fragile_session_output" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("fragile_session_output")}
    if "thinking_output" not in columns:
        connection.execute(text("ALTER TABLE fragile_session_output ADD COLUMN thinking_output VARCHAR"))


def _migrate_session_output_trace(connection: object) -> None:
    """Add the normalized trace payload column to legacy session output databases."""
    inspector = inspect(connection)
    if "fragile_session_output" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("fragile_session_output")}
    if "trace_payload" not in columns:
        connection.execute(text("ALTER TABLE fragile_session_output ADD COLUMN trace_payload VARCHAR"))


engine = get_engine()

# Keep these resources at runtime scope.  Model compatibility methods can still
# obtain the factory, but they no longer repeat schema inspection.
_session_factories: dict[AsyncEngine, async_sessionmaker[AsyncSession]] = {}
_initialized_engines: set[AsyncEngine] = set()
_initialization_lock = Lock()


async def get_initialized_session_factory(
    async_engine: AsyncEngine | None = None,
) -> async_sessionmaker[AsyncSession]:
    """Return the runtime session factory, initializing a database once."""
    database_engine = async_engine or engine
    async with _initialization_lock:
        if database_engine not in _initialized_engines:
            await create_tables(database_engine)
            _initialized_engines.add(database_engine)
        factory = _session_factories.get(database_engine)
        if factory is None:
            factory = async_sessionmaker(database_engine, expire_on_commit=False)
            _session_factories[database_engine] = factory
        return factory


async def dispose_database(async_engine: AsyncEngine | None = None) -> None:
    """Dispose a runtime engine and forget its cached resources."""
    database_engine = async_engine or engine
    await database_engine.dispose()
    _session_factories.pop(database_engine, None)
    _initialized_engines.discard(database_engine)
