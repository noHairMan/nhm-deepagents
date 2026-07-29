from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
import typer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import RadioList
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fragile.commands.interactive.commands.history import (
    HISTORY_STYLE,
    HistoryCommand,
    choose_history,
    format_elapsed_time,
    list_history,
    select_history,
)
from fragile.models import Base, ConversationHistory, SessionState
from fragile.models.constants import CommandResult


class TestHistoryCommand:
    def test_select_history_hides_numbers(self) -> None:
        first = UUID(int=1)
        application = MagicMock()
        application.run.return_value = first
        with (
            patch(
                "fragile.commands.interactive.commands.history.RadioList",
                wraps=RadioList,
            ) as radio_list_factory,
            patch("fragile.commands.interactive.commands.history.Application", return_value=application),
        ):
            assert select_history("Select:", [(first, "对话")], KeyBindings(), HISTORY_STYLE, "", True) == first
        assert radio_list_factory.call_args.kwargs["show_numbers"] is False
        assert HISTORY_STYLE.get_attrs_for_style_str("class:selected-option").color == "ansigreen"

    def test_history_command_handles_prompt_directly(self) -> None:
        state = SessionState(thread_id=UUID(int=1), prompt_session=object())
        with (
            patch(
                "fragile.commands.interactive.commands.history.list_history",
                new_callable=AsyncMock,
                return_value=[],
            ),
            patch("fragile.commands.interactive.commands.history.choose_history", return_value=None),
        ):
            assert HistoryCommand().handle("ordinary prompt", state) is CommandResult.CONTINUE

    def test_choose_history_returns_selected_thread(self) -> None:
        first = UUID(int=1)
        selector = MagicMock(return_value=first)
        with patch("fragile.commands.interactive.commands.history.typer.echo"):
            assert choose_history([(first, "第一次对话")], selector) == first
        selector.assert_called_once_with(
            "Select a conversation:",
            options=[(first, "第一次对话")],
            key_bindings=selector.call_args.kwargs["key_bindings"],
            style=selector.call_args.kwargs["style"],
            symbol="",
            enable_interrupt=False,
        )

    def test_choose_history_esc_cancels_selection(self) -> None:
        first = UUID(int=1)
        selector = MagicMock(return_value=first)
        choose_history([(first, "第一次对话")], selector)
        key_bindings = selector.call_args.kwargs["key_bindings"]
        event = MagicMock()
        key_bindings.get_bindings_for_keys(("escape",))[0].handler(event)
        event.app.exit.assert_called_once()
        assert isinstance(event.app.exit.call_args.kwargs["exception"], typer.Abort)

    def test_choose_history_returns_none_without_threads(self) -> None:
        selector = MagicMock()
        with patch("fragile.commands.interactive.commands.history.typer.echo"):
            assert choose_history([], selector) is None
        selector.assert_not_called()

    @pytest.mark.parametrize("cancel", [typer.Abort])
    def test_choose_history_returns_none_when_cancelled(self, cancel: type[BaseException]) -> None:
        first = UUID(int=1)
        selector = MagicMock(side_effect=cancel)
        assert choose_history([(first, "第一次对话")], selector) is None

    @pytest.mark.asyncio
    async def test_list_history_returns_titles(self, tmp_path, monkeypatch) -> None:
        first = UUID(int=1)
        database_path = tmp_path / "history.db"
        engine = create_engine(f"sqlite:///{database_path}")
        Base.metadata.create_all(engine)
        monkeypatch.setattr("fragile.commands.interactive.commands.history.engine", engine)

        monkeypatch.setattr("fragile.models.history.engine", engine)
        ConversationHistory.register_conversation(first, "第一次对话")
        assert await list_history() == [(first, "第一次对话    just now")]

    @pytest.mark.asyncio
    async def test_list_history_returns_newest_conversations_first(self, tmp_path, monkeypatch) -> None:
        engine = create_engine(f"sqlite:///{tmp_path / 'history.db'}")
        Base.metadata.create_all(engine)
        monkeypatch.setattr("fragile.commands.interactive.commands.history.engine", engine)
        older = ConversationHistory(thread_id=str(UUID(int=1)), title="较早对话")
        newer = ConversationHistory(thread_id=str(UUID(int=2)), title="较新对话")
        created_at = datetime.now()
        older.update_time = created_at - timedelta(days=1)
        newer.update_time = created_at
        with Session(engine) as session:
            session.add_all([older, newer])
            session.commit()

        assert await list_history() == [
            (UUID(int=2), "较新对话    just now"),
            (UUID(int=1), "较早对话    1 day ago"),
        ]

    @pytest.mark.asyncio
    async def test_list_history_returns_empty_for_empty_database(self, tmp_path, monkeypatch) -> None:
        engine = create_engine(f"sqlite:///{tmp_path / 'history.db'}")
        Base.metadata.create_all(engine)
        monkeypatch.setattr("fragile.commands.interactive.commands.history.engine", engine)
        assert await list_history() == []

    @pytest.mark.asyncio
    async def test_list_history_reads_existing_schema(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "history.db"
        engine = create_engine(f"sqlite:///{database_path}")
        Base.metadata.create_all(engine)
        monkeypatch.setattr("fragile.commands.interactive.commands.history.engine", engine)
        with Session(engine) as session:
            session.add(ConversationHistory(thread_id=str(UUID(int=3)), title="已有对话"))
            session.commit()
        engine.dispose()
        assert await list_history() == [(UUID(int=3), "已有对话    just now")]

    @pytest.mark.parametrize(
        ("elapsed", "expected"),
        [
            (timedelta(seconds=30), "just now"),
            (timedelta(minutes=1), "1 minute ago"),
            (timedelta(hours=2), "2 hours ago"),
            (timedelta(days=3), "3 days ago"),
        ],
    )
    def test_format_elapsed_time(self, elapsed: timedelta, expected: str) -> None:
        now = datetime(2026, 1, 1)
        assert format_elapsed_time(now - elapsed, now) == expected

    def test_history_command_keeps_state_when_selection_is_cancelled(self) -> None:
        state = SessionState(thread_id=UUID(int=1), prompt_session=object())
        with (
            patch(
                "fragile.commands.interactive.commands.history.list_history",
                new_callable=AsyncMock,
                return_value=[(UUID(int=2), "第二次对话")],
            ),
            patch(
                "fragile.commands.interactive.commands.history.choose_history",
                return_value=None,
            ),
        ):
            assert HistoryCommand().handle("/history", state) is CommandResult.CONTINUE
        assert state.thread_id == UUID(int=1)
