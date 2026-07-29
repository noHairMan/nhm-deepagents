from sqlalchemy import select
from sqlalchemy.orm import Session

from fragile.models import Base, ConversationHistory
from fragile.models.base import get_engine


class TestDatabase:
    def test_get_engine_creates_parent_directory(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "nested" / "history.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)
        engine = get_engine()
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            assert session.scalar(select(ConversationHistory)) is None
        engine.dispose()
