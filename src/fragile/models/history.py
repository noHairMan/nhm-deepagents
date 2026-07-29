"""Conversation history models and persistence helpers."""

from datetime import datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy import DateTime, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from fragile.utils.uid import to_hex
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


class ConversationHistory(Base):
    """Persisted title for a conversation thread."""

    __tablename__ = "fragile_conversation_history"

    thread_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)


def _database_path() -> Path:
    return Path(settings.CHECKPOINT[CheckpointType.SQLITE]["path"])


def register_conversation(thread_id: UUID, title: str) -> None:
    """Persist the first title for a conversation."""
    thread_id_hex = to_hex(thread_id)
    path = _database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{path}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        conversation = session.scalar(select(ConversationHistory).where(ConversationHistory.thread_id == thread_id_hex))
        if conversation is None:
            session.add(ConversationHistory(thread_id=thread_id_hex, title=title))
            session.commit()
    engine.dispose()
