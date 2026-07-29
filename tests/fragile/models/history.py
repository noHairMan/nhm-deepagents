from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import fragile.models.history as history_module
from fragile.models import Base, ConversationHistory


class TestHistory:
    def test_register_stores_hex_thread_id(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "history.db"
        engine = create_engine(f"sqlite:///{database_path}")
        Base.metadata.create_all(engine)
        monkeypatch.setattr(history_module, "engine", engine)
        thread_id = UUID("12345678-1234-5678-1234-567812345678")
        ConversationHistory.register_conversation(thread_id, "标题")
        engine = create_engine(f"sqlite:///{database_path}")
        with Session(engine) as session:
            stored = session.scalar(select(ConversationHistory.thread_id))
        engine.dispose()
        assert stored == thread_id.hex

    def test_base_fields_are_populated(self, tmp_path) -> None:
        engine = create_engine(f"sqlite:///{tmp_path / 'history.db'}")
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            conversation = ConversationHistory(thread_id="thread", title="标题")
            session.add(conversation)
            session.commit()
            assert conversation.id is not None
            assert conversation.create_time is not None
            assert conversation.update_time is not None
        engine.dispose()

    def test_register_keeps_first_title(self, tmp_path, monkeypatch) -> None:
        engine = create_engine(f"sqlite:///{tmp_path / 'history.db'}")
        Base.metadata.create_all(engine)
        monkeypatch.setattr(history_module, "engine", engine)
        thread_id = UUID(int=1)
        ConversationHistory.register_conversation(thread_id, "第一次对话")
        ConversationHistory.register_conversation(thread_id, "后续消息")

    def test_list_normalizes_existing_uuid_thread_id(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "history.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)
        engine = create_engine(f"sqlite:///{database_path}")
        Base.metadata.create_all(engine)
        thread_id = UUID("00000000-0000-0000-0000-000000000003")
        with Session(engine) as session:
            session.add(ConversationHistory(thread_id=str(thread_id), title="旧标题"))
            session.commit()
        engine.dispose()
