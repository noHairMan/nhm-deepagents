"""Conversation history models and persistence helpers."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, delete, select
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


class SessionOutput(Base):
    """Persisted terminal output for one completed conversation turn."""

    __tablename__ = "fragile_session_output"

    thread_id: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    user_input: Mapped[str] = mapped_column(String, nullable=False)
    assistant_output: Mapped[str] = mapped_column(String, nullable=False)
    style_payload: Mapped[str] = mapped_column(String, nullable=False, default="")
    thinking_output: Mapped[str | None] = mapped_column(String, nullable=True)
    trace_payload: Mapped[str | None] = mapped_column(String, nullable=True)

    @classmethod
    async def save_output(
        cls,
        thread_id: UUID,
        user_input: str,
        assistant_output: str,
        style_payload: str = "",
        thinking_output: str | None = None,
        trace_payload: str | None = None,
    ) -> None:
        """Save a completed turn without blocking the event loop."""
        session_factory = await get_initialized_session_factory()
        async with session_factory() as session:
            session.add(
                cls(
                    thread_id=to_hex(thread_id),
                    user_input=user_input,
                    assistant_output=assistant_output,
                    style_payload=style_payload,
                    thinking_output=thinking_output,
                    trace_payload=trace_payload,
                )
            )
            await session.commit()

    @classmethod
    async def list_for_thread(cls, thread_id: UUID) -> list[SessionOutput]:
        """Return output records in their insertion order."""
        session_factory = await get_initialized_session_factory()
        async with session_factory() as session:
            result = await session.scalars(select(cls).where(cls.thread_id == to_hex(thread_id)).order_by(cls.id))
            return list(result)

    @classmethod
    async def delete_for_thread(cls, thread_id: UUID) -> int:
        """Delete all output records belonging to a thread."""
        session_factory = await get_initialized_session_factory()
        async with session_factory() as session:
            result = await session.execute(delete(cls).where(cls.thread_id == to_hex(thread_id)))
            await session.commit()
            return result.rowcount or 0
