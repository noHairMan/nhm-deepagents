import pytest
from sqlalchemy import create_engine, inspect, text

from fragile.models.base import _migrate_account_provider, create_tables, get_engine


class TestDatabase:
    @pytest.mark.asyncio
    async def test_create_tables(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "nested" / "history.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)
        async_engine = get_engine()
        await create_tables(async_engine)
        await async_engine.dispose()
        assert database_path.exists()

    def test_migrate_account_provider_adds_missing_column(self, tmp_path) -> None:
        database_path = tmp_path / "legacy.db"
        sync_engine = create_engine(f"sqlite:///{database_path}")
        with sync_engine.begin() as connection:
            connection.execute(text("CREATE TABLE fragile_account (id INTEGER PRIMARY KEY)"))
            _migrate_account_provider(connection)
            columns = {column["name"] for column in inspect(connection).get_columns("fragile_account")}
        sync_engine.dispose()
        assert "provider" in columns

    def test_migrate_account_provider_ignores_missing_account_table(self, tmp_path) -> None:
        sync_engine = create_engine(f"sqlite:///{tmp_path / 'empty.db'}")
        with sync_engine.begin() as connection:
            _migrate_account_provider(connection)
        sync_engine.dispose()
