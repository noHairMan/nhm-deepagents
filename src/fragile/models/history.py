"""Conversation history models and persistence helpers."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column

from fragile.models.base import Base, get_initialized_session_factory
from fragile.utils.uid import to_hex


class ConversationHistory(Base):
    """Persisted title for a conversation thread."""

    __tablename__ = "fragile_conversation_history"

    thread_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)

    @staticmethod
    def format_title(title: str) -> str:
        """Keep persisted titles concise while preserving their beginning."""
        return f"{title[:12]}..." if len(title) > 12 else title

    @classmethod
    async def register_conversation(cls, thread_id: UUID, title: str) -> None:
        """Persist a conversation title without blocking the event loop."""
        thread_id_hex = to_hex(thread_id)
        formatted_title = cls.format_title(title)
        session_factory = await get_initialized_session_factory()
        async with session_factory() as session:
            conversation = await session.scalar(select(cls).where(cls.thread_id == thread_id_hex))
            if conversation is None:
                session.add(cls(thread_id=thread_id_hex, title=formatted_title))
            else:
                conversation.update_time = datetime.now()
            await session.commit()
