"""Purge persisted Fragile session data."""

from sqlalchemy import delete, inspect
from sqlalchemy.ext.asyncio import AsyncSession

from fragile.models.base import engine
from fragile.models.history import ConversationHistory, SessionOutput


async def purge_sessions() -> int:
    """Delete rows from the conversation history table."""
    table = ConversationHistory.__table__
    output_table = SessionOutput.__table__
    async with engine.connect() as connection:
        tables = await connection.run_sync(lambda sync_connection: inspect(sync_connection).get_table_names())
    if table.name not in tables:
        return 0
    async with AsyncSession(engine) as session:
        result = await session.execute(delete(table))
        deleted = result.rowcount or 0
        if output_table.name in tables:
            await session.execute(delete(output_table))
        await session.commit()
    return deleted
