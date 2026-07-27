from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
import typer

from fragile.commands.interactive.commands.base import CommandResult, SessionState
from fragile.commands.interactive.commands.history import (
    choose_history,
    handle_history,
    is_history_command,
    list_history,
    list_thread_ids,
)


class TestHistoryCommand:
    def test_is_history_command_ignores_case_and_whitespace(self) -> None:
        assert is_history_command("  /HISTORY  ") is True
        assert is_history_command("history") is False

    @pytest.mark.asyncio
    async def test_list_thread_ids_returns_distinct_ids(self) -> None:
        first = UUID(int=1)
        second = UUID(int=2)
        checkpoints = [
            type("Checkpoint", (), {"config": {"configurable": {"thread_id": str(second)}}})(),
            type("Checkpoint", (), {"config": {"configurable": {"thread_id": str(first)}}})(),
            type("Checkpoint", (), {"config": {"configurable": {"thread_id": str(second)}}})(),
        ]

        async def alist(self: object, config: object) -> object:
            for checkpoint in checkpoints:
                yield checkpoint

        checkpointer = type("Checkpointer", (), {"alist": alist})()
        context = MagicMock()
        context.return_value.__aenter__ = AsyncMock(return_value=checkpointer)
        context.return_value.__aexit__ = AsyncMock(return_value=None)
        assert await list_thread_ids(context) == [first, second]

    @pytest.mark.asyncio
    async def test_list_thread_ids_ignores_missing_thread_id(self) -> None:
        checkpoint = type("Checkpoint", (), {"config": {"configurable": {}}})()

        async def alist(self: object, config: object) -> object:
            yield checkpoint

        checkpointer = type("Checkpointer", (), {"alist": alist})()
        context = MagicMock()
        context.return_value.__aenter__ = AsyncMock(return_value=checkpointer)
        context.return_value.__aexit__ = AsyncMock(return_value=None)
        assert await list_thread_ids(context) == []

    @pytest.mark.asyncio
    async def test_list_thread_ids_returns_empty_without_checkpointer(self) -> None:
        context = MagicMock()
        context.return_value.__aenter__ = AsyncMock(return_value=None)
        context.return_value.__aexit__ = AsyncMock(return_value=None)
        assert await list_thread_ids(context) == []

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
    async def test_list_history_returns_titles(self) -> None:
        first = UUID(int=1)
        checkpoint = type(
            "Checkpoint",
            (),
            {
                "config": {"configurable": {"thread_id": str(first)}},
                "checkpoint": {"channel_values": {"messages": [{"type": "human", "content": "第一次对话"}]}},
            },
        )()

        async def alist(self: object, config: object) -> object:
            yield checkpoint

        checkpointer = type("Checkpointer", (), {"alist": alist})()
        context = MagicMock()
        context.return_value.__aenter__ = AsyncMock(return_value=checkpointer)
        context.return_value.__aexit__ = AsyncMock(return_value=None)
        assert await list_history(context) == [(first, "第一次对话")]

    def test_handle_history_keeps_state_when_selection_is_cancelled(self) -> None:
        state = SessionState(UUID(int=1), object())
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
            assert handle_history("/history", state) is CommandResult.CONTINUE
        assert state.thread_id == UUID(int=1)
