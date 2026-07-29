"""Database setup and shared ORM infrastructure for Fragile."""

from datetime import datetime
from pathlib import Path

from sqlalchemy import DateTime, Engine, create_engine
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


engine = get_engine()
Base.metadata.create_all(engine)
