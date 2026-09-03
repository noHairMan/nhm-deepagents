from uuid import UUID

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from fragile.commands.interactive.trace import TraceEvent, trace_from_json
from fragile.models import Base, ConversationHistory, SessionOutput
from fragile.models.base import create_tables, get_engine


class TestHistory:
    def test_format_title_truncates_long_titles(self) -> None:
        assert ConversationHistory.format_title("一二三四五六七八九十百千万") == "一二三四五六七八九十百千..."

    def test_format_title_keeps_short_titles(self) -> None:
        assert ConversationHistory.format_title("短标题") == "短标题"

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
        async_engine = get_engine()
        monkeypatch.setattr("fragile.models.base.engine", async_engine)
        await create_tables(async_engine)
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
    async def test_register_conversation_truncates_title(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "long-history.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)
        async_engine = get_engine()
        monkeypatch.setattr("fragile.models.base.engine", async_engine)
        await create_tables(async_engine)

        await ConversationHistory.register_conversation(UUID(int=4), "1234567890123")
        await async_engine.dispose()
        engine = create_engine(f"sqlite:///{database_path}")
        with Session(engine) as session:
            stored = session.scalar(select(ConversationHistory))
        engine.dispose()
        assert stored is not None
        assert stored.title == "123456789012..."

    @pytest.mark.asyncio
    async def test_register_conversation_initializes_missing_table(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "new-history.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)
        monkeypatch.setattr("fragile.models.base.engine", get_engine())

        await ConversationHistory.register_conversation(UUID(int=3), "新对话")

        engine = create_engine(f"sqlite:///{database_path}")
        with Session(engine) as session:
            stored = session.scalar(select(ConversationHistory))
        engine.dispose()
        assert stored is not None
        assert stored.title == "新对话"

    @pytest.mark.asyncio
    async def test_session_output_round_trip_preserves_order_style_and_thinking(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "output.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)
        async_engine = get_engine()
        monkeypatch.setattr("fragile.models.base.engine", async_engine)
        thread_id = UUID(int=5)

        await SessionOutput.save_output(
            thread_id,
            "第一问",
            "[bold]第一答[/bold]",
            "markup",
            thinking_output="第一想法",
            trace_payload='[{"sequence": 1, "kind": "text", "content": "第一答"}]',
        )
        await SessionOutput.save_output(thread_id, "第二问", "第二答")
        records = await SessionOutput.list_for_thread(thread_id)

        assert [(record.user_input, record.assistant_output) for record in records] == [
            ("第一问", "[bold]第一答[/bold]"),
            ("第二问", "第二答"),
        ]
        assert records[0].style_payload == "markup"
        assert records[0].thinking_output == "第一想法"
        assert trace_from_json(records[0].trace_payload) == [TraceEvent(1, "text", content="第一答")]
        assert records[1].thinking_output is None
        await async_engine.dispose()

    @pytest.mark.asyncio
    async def test_session_output_delete_for_thread(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "delete-output.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)
        async_engine = get_engine()
        monkeypatch.setattr("fragile.models.base.engine", async_engine)
        await SessionOutput.save_output(UUID(int=6), "问题", "回答")

        assert await SessionOutput.delete_for_thread(UUID(int=6)) == 1
        assert await SessionOutput.list_for_thread(UUID(int=6)) == []
        await async_engine.dispose()
