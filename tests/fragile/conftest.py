from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from fragile.models.base import dispose_database, get_engine, get_initialized_session_factory


@pytest_asyncio.fixture(scope="function")
async def session_factory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    # Setup: Use a unique temporary database for each test to ensure isolation
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", db_path)

    # Get the engine
    engine = get_engine()
    monkeypatch.setattr("fragile.models.base.engine", engine)

    factory = await get_initialized_session_factory(engine)

    yield factory

    # Teardown: Dispose the database and clear resources
    await dispose_database(engine)
