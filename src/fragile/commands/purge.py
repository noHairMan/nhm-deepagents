"""Purge persisted Fragile session data."""

from sqlalchemy import delete, inspect
from sqlalchemy.ext.asyncio import AsyncSession

from fragile.models.base import engine
from fragile.models.history import ConversationHistory


async def purge_sessions() -> int:
    """Delete rows from the conversation history table."""
    table = ConversationHistory.__table__
    async with engine.connect() as connection:
        has_table = await connection.run_sync(lambda sync_connection: inspect(sync_connection).has_table(table.name))
    if not has_table:
        return 0
    async with AsyncSession(engine) as session:
        result = await session.execute(delete(table))
        deleted = result.rowcount or 0
        await session.commit()
    return deleted
