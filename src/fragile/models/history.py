"""Conversation history models and persistence helpers."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from fragile.models.base import Base, engine
from fragile.utils.uid import to_hex


class ConversationHistory(Base):
    """Persisted title for a conversation thread."""

    __tablename__ = "fragile_conversation_history"

    thread_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)

    @classmethod
    def register_conversation(cls, thread_id: UUID, title: str) -> None:
        """Persist a conversation title and refresh its activity time."""
        thread_id_hex = to_hex(thread_id)
        with Session(engine) as session:
            conversation = session.scalar(select(cls).where(cls.thread_id == thread_id_hex))
            if conversation is None:
                session.add(cls(thread_id=thread_id_hex, title=title))
            else:
                conversation.update_time = datetime.now()
            session.commit()
