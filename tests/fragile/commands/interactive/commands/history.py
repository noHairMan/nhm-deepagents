from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest

from fragile.commands.interactive.commands.history import (
    choose_history,
    is_history_command,
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

    def test_choose_history_accepts_number_and_uuid(self) -> None:
        first = UUID(int=1)
        session = object()
        with patch("fragile.commands.interactive.commands.history.typer.echo"):
            assert choose_history(session, [first], lambda _: "1") == first
            assert choose_history(session, [first], lambda _: str(first)) == first

    def test_choose_history_rejects_invalid_or_unknown_values(self) -> None:
        first = UUID(int=1)
        session = object()
        with patch("fragile.commands.interactive.commands.history.typer.echo"):
            assert choose_history(session, [first], lambda _: "bad") is None
            assert choose_history(session, [first], lambda _: "2") is None
            assert choose_history(session, [first], lambda _: str(UUID(int=2))) is None
            assert choose_history(session, [], lambda _: "1") is None
