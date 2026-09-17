"""Persistence operations for conversation titles."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from fragile.models.history import ConversationHistory
from fragile.utils.uid import to_hex


class ConversationRepository:
    """Persist and query conversation titles."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def register(self, thread_id: UUID, title: str) -> None:
        """Create a title or update its timestamp."""
        async with self.session_factory() as session:
            conversation = await session.scalar(
                select(ConversationHistory).where(ConversationHistory.thread_id == to_hex(thread_id))
            )
            if conversation is None:
                session.add(
                    ConversationHistory(
                        thread_id=to_hex(thread_id),
                        title=ConversationHistory.format_title(title),
                    )
                )
            else:
                conversation.update_time = datetime.now()
            await session.commit()

    async def list(self) -> list[ConversationHistory]:
        """Return conversations ordered by most recent update."""
        async with self.session_factory() as session:
            result = await session.scalars(select(ConversationHistory).order_by(ConversationHistory.update_time.desc()))
            return list(result.all())
