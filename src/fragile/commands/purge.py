"""Purge persisted Fragile session data."""

from sqlalchemy import delete, inspect
from sqlalchemy.orm import Session

from fragile.models.base import engine
from fragile.models.history import ConversationHistory


def purge_sessions() -> int:
    """Delete rows from the conversation history table."""
    table = ConversationHistory.__table__
    if not inspect(engine).has_table(table.name):
        return 0
    with Session(engine) as session:
        deleted = session.execute(delete(table)).rowcount
        session.commit()
    return deleted
