from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
import typer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fragile.commands.interactive.commands.history import HistoryCommand, choose_history, list_history
from fragile.models import Base, ConversationHistory, SessionState
from fragile.models.constants import CommandResult


class TestHistoryCommand:
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
        monkeypatch.setattr("fragile.models.history.settings.CHECKPOINT.sqlite.path", tmp_path / "history.db")
        from fragile.models.history import register_conversation

        register_conversation(first, "第一次对话")
        assert await list_history() == [(first, "第一次对话")]

    @pytest.mark.asyncio
    async def test_list_history_returns_empty_for_missing_database(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr("fragile.models.history.settings.CHECKPOINT.sqlite.path", tmp_path / "missing.db")
        assert await list_history() == []

    @pytest.mark.asyncio
    async def test_list_history_reads_existing_schema(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "history.db"
        monkeypatch.setattr("fragile.models.history.settings.CHECKPOINT.sqlite.path", database_path)
        engine = create_engine(f"sqlite:///{database_path}")
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            session.add(ConversationHistory(thread_id=str(UUID(int=3)), title="已有对话"))
            session.commit()
        engine.dispose()
        assert await list_history() == [(UUID(int=3), "已有对话")]

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
