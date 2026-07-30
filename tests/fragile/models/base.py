import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from fragile.models import Base, ConversationHistory
from fragile.models.base import create_tables_async, get_async_engine, get_engine


class TestDatabase:
    def test_get_engine_creates_parent_directory(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "nested" / "history.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)
        engine = get_engine()
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            assert session.scalar(select(ConversationHistory)) is None
        engine.dispose()

    @pytest.mark.asyncio
    async def test_create_tables_async(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "nested" / "history.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)
        async_engine = get_async_engine()
        await create_tables_async(async_engine)
        await async_engine.dispose()
        assert database_path.exists()
