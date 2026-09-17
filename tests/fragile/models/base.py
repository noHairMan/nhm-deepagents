from unittest.mock import AsyncMock

import pytest
from sqlalchemy import create_engine, inspect, text

from fragile.models.base import (
    _initialized_engines,
    _migrate_account_model,
    _migrate_account_provider,
    _migrate_session_output_thinking,
    _migrate_session_output_trace,
    _session_factories,
    create_tables,
    dispose_database,
    get_engine,
    get_initialized_session_factory,
)


class TestDatabase:
    @pytest.mark.asyncio
    async def test_create_tables(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "nested" / "history.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)
        async_engine = get_engine()
        await create_tables(async_engine)
        await async_engine.dispose()
        assert database_path.exists()

    @pytest.mark.asyncio
    async def test_initialized_session_factory_reuses_schema_initialization(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", tmp_path / "cached.db")
        async_engine = get_engine()
        initializer = AsyncMock()
        monkeypatch.setattr("fragile.models.base.create_tables", initializer)
        monkeypatch.setattr("fragile.models.base.engine", async_engine)

        first = await get_initialized_session_factory()
        second = await get_initialized_session_factory()

        assert first is second
        initializer.assert_awaited_once_with(async_engine)
        await async_engine.dispose()

    @pytest.mark.asyncio
    async def test_dispose_database_clears_caches(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", tmp_path / "dispose.db")
        async_engine = get_engine()
        monkeypatch.setattr("fragile.models.base.engine", async_engine)

        # Initialize the engine and factory
        factory = await get_initialized_session_factory()
        assert async_engine in _initialized_engines
        assert async_engine in _session_factories
        assert _session_factories[async_engine] is factory

        # Dispose and verify caches are cleared
        await dispose_database()
        assert async_engine not in _initialized_engines
        assert async_engine not in _session_factories

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

    def test_migrate_account_model_adds_missing_column_idempotently(self, tmp_path) -> None:
        database_path = tmp_path / "legacy-model.db"
        sync_engine = create_engine(f"sqlite:///{database_path}")
        with sync_engine.begin() as connection:
            connection.execute(text("CREATE TABLE fragile_account (id INTEGER PRIMARY KEY)"))
            _migrate_account_model(connection)
            _migrate_account_model(connection)
            columns = {column["name"] for column in inspect(connection).get_columns("fragile_account")}
        sync_engine.dispose()
        assert "model" in columns

    def test_migrate_account_model_ignores_missing_account_table(self, tmp_path) -> None:
        sync_engine = create_engine(f"sqlite:///{tmp_path / 'empty-model.db'}")
        with sync_engine.begin() as connection:
            _migrate_account_model(connection)
        sync_engine.dispose()

    def test_migrate_session_output_thinking_adds_missing_column_idempotently(self, tmp_path) -> None:
        database_path = tmp_path / "legacy-output.db"
        sync_engine = create_engine(f"sqlite:///{database_path}")
        with sync_engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE TABLE fragile_session_output "
                    "(id INTEGER PRIMARY KEY, user_input VARCHAR NOT NULL, "
                    "assistant_output VARCHAR NOT NULL, style_payload VARCHAR NOT NULL)"
                )
            )
            _migrate_session_output_thinking(connection)
            _migrate_session_output_thinking(connection)
            columns = {column["name"] for column in inspect(connection).get_columns("fragile_session_output")}
        sync_engine.dispose()
        assert "thinking_output" in columns

    def test_migrate_session_output_thinking_ignores_missing_table(self, tmp_path) -> None:
        sync_engine = create_engine(f"sqlite:///{tmp_path / 'empty-output.db'}")
        with sync_engine.begin() as connection:
            _migrate_session_output_thinking(connection)
        sync_engine.dispose()

    def test_migrate_session_output_trace_adds_missing_column_idempotently(self, tmp_path) -> None:
        database_path = tmp_path / "legacy-trace.db"
        sync_engine = create_engine(f"sqlite:///{database_path}")
        with sync_engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE TABLE fragile_session_output "
                    "(id INTEGER PRIMARY KEY, user_input VARCHAR NOT NULL, "
                    "assistant_output VARCHAR NOT NULL, style_payload VARCHAR NOT NULL)"
                )
            )
            _migrate_session_output_trace(connection)
            _migrate_session_output_trace(connection)
            columns = {column["name"] for column in inspect(connection).get_columns("fragile_session_output")}
        sync_engine.dispose()
        assert "trace_payload" in columns

    def test_migrate_session_output_trace_ignores_missing_table(self, tmp_path) -> None:
        sync_engine = create_engine(f"sqlite:///{tmp_path / 'empty-trace.db'}")
        with sync_engine.begin() as connection:
            _migrate_session_output_trace(connection)
        sync_engine.dispose()
