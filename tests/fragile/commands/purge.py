from sqlalchemy import create_engine, func, select, text

from fragile.commands.purge import purge_sessions
from fragile.models.history import ConversationHistory


class TestPurgeSessions:
    def test_purge_sessions_deletes_only_conversation_history(self, tmp_path, monkeypatch) -> None:
        engine = create_engine(f"sqlite:///{tmp_path / 'sessions.db'}")
        ConversationHistory.__table__.create(engine)
        with engine.begin() as connection:
            connection.execute(text("CREATE TABLE unrelated (id INTEGER PRIMARY KEY)"))
            connection.execute(ConversationHistory.__table__.insert().values(thread_id="thread", title="title"))
            connection.execute(text("INSERT INTO unrelated VALUES (1)"))
        monkeypatch.setattr("fragile.commands.purge.engine", engine)

        assert purge_sessions() == 1
        with engine.connect() as connection:
            count = select(func.count()).select_from(ConversationHistory.__table__)
            assert connection.execute(count).scalar_one() == 0
            assert connection.execute(text("SELECT COUNT(*) FROM unrelated")).scalar_one() == 1

    def test_purge_sessions_handles_empty_database(self, tmp_path, monkeypatch) -> None:
        engine = create_engine(f"sqlite:///{tmp_path / 'sessions.db'}")
        monkeypatch.setattr("fragile.commands.purge.engine", engine)

        assert purge_sessions() == 0
