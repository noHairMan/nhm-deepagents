"""Conversation history models and persistence helpers."""

from datetime import datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy import DateTime, String, create_engine, inspect, select, text
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


def _ensure_schema(engine: object) -> None:
    """Create the ORM schema and migrate the legacy history table if needed."""
    Base.metadata.create_all(engine)
    columns = {column["name"] for column in inspect(engine).get_columns(ConversationHistory.__tablename__)}
    required_columns = {"id", "create_time", "update_time"}
    if required_columns.issubset(columns):
        with engine.begin() as connection:
            rows = connection.execute(text("SELECT id, thread_id FROM fragile_conversation_history")).fetchall()
            for row_id, thread_id in rows:
                normalized_thread_id = to_hex(thread_id)
                if normalized_thread_id != thread_id:
                    connection.execute(
                        text("UPDATE fragile_conversation_history SET thread_id = :thread_id WHERE id = :id"),
                        {"id": row_id, "thread_id": normalized_thread_id},
                    )
        return
    with engine.begin() as connection:
        connection.execute(
            text("ALTER TABLE fragile_conversation_history RENAME TO fragile_conversation_history_legacy")
        )
        Base.metadata.create_all(connection)
        rows = connection.execute(text("SELECT thread_id, title FROM fragile_conversation_history_legacy")).fetchall()
        for thread_id, title in rows:
            connection.execute(
                text(
                    "INSERT INTO fragile_conversation_history (thread_id, title, create_time, update_time) "
                    "VALUES (:thread_id, :title, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                ),
                {"thread_id": to_hex(thread_id), "title": title},
            )
        connection.execute(text("DROP TABLE fragile_conversation_history_legacy"))


def register_conversation(thread_id: UUID, title: str) -> None:
    """Persist the first title for a conversation."""
    thread_id_hex = to_hex(thread_id)
    path = _database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{path}")
    _ensure_schema(engine)
    with Session(engine) as session:
        conversation = session.scalar(select(ConversationHistory).where(ConversationHistory.thread_id == thread_id_hex))
        if conversation is None:
            session.add(ConversationHistory(thread_id=thread_id_hex, title=title))
            session.commit()
    engine.dispose()
