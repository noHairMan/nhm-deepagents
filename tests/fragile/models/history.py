from uuid import UUID

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from fragile.models import Base, ConversationHistory
from fragile.models.base import create_tables_async, get_async_engine


class TestHistory:
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

    @pytest.mark.asyncio
    async def test_register_conversation_stores_and_updates(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "history.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)
        async_engine = get_async_engine()
        await create_tables_async(async_engine)
        thread_id = UUID(int=2)
        await ConversationHistory.register_conversation(thread_id, "异步对话")
        await ConversationHistory.register_conversation(thread_id, "后续消息")
        await async_engine.dispose()
        engine = create_engine(f"sqlite:///{database_path}")
        with Session(engine) as session:
            stored = session.scalar(select(ConversationHistory))
        engine.dispose()
        assert stored is not None
        assert stored.thread_id == thread_id.hex
        assert stored.title == "异步对话"

    @pytest.mark.asyncio
    async def test_register_conversation_initializes_missing_table(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "new-history.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)

        await ConversationHistory.register_conversation(UUID(int=3), "新对话")

        engine = create_engine(f"sqlite:///{database_path}")
        with Session(engine) as session:
            stored = session.scalar(select(ConversationHistory))
        engine.dispose()
        assert stored is not None
        assert stored.title == "新对话"
