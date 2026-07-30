import pytest

from fragile.models.base import create_tables, get_engine


class TestDatabase:
    @pytest.mark.asyncio
    async def test_create_tables(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "nested" / "history.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)
        async_engine = get_engine()
        await create_tables(async_engine)
        await async_engine.dispose()
        assert database_path.exists()
