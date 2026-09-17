"""Purge persisted Fragile session data."""

from fragile.models.base import engine as default_engine
from fragile.models.base import get_initialized_session_factory

engine = default_engine


async def purge_sessions() -> int:
    """Delete rows from the conversation history table."""
    from fragile.repositories.session import SessionRepository

    session_factory = await get_initialized_session_factory(engine)
    return await SessionRepository(session_factory).purge()
