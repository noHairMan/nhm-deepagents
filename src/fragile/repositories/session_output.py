"""Persistence operations for completed session output."""

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from fragile.models.history import SessionOutput
from fragile.utils.uid import to_hex


class SessionOutputRepository:
    """Persist, query, and delete completed turns."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def save(
        self,
        thread_id: UUID,
        user_input: str,
        assistant_output: str,
        style_payload: str = "",
        thinking_output: str | None = None,
        trace_payload: str | None = None,
    ) -> None:
        """Save one completed turn."""
        async with self.session_factory() as session:
            session.add(
                SessionOutput(
                    thread_id=to_hex(thread_id),
                    user_input=user_input,
                    assistant_output=assistant_output,
                    style_payload=style_payload,
                    thinking_output=thinking_output,
                    trace_payload=trace_payload,
                )
            )
            await session.commit()

    async def list_for_thread(self, thread_id: UUID) -> list[SessionOutput]:
        """Return output records in insertion order."""
        async with self.session_factory() as session:
            result = await session.scalars(
                select(SessionOutput).where(SessionOutput.thread_id == to_hex(thread_id)).order_by(SessionOutput.id)
            )
            return list(result)

    async def delete_for_thread(self, thread_id: UUID) -> int:
        """Delete all output records belonging to a thread."""
        async with self.session_factory() as session:
            result = await session.execute(delete(SessionOutput).where(SessionOutput.thread_id == to_hex(thread_id)))
            await session.commit()
            return result.rowcount or 0
