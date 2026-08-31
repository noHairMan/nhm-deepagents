from unittest.mock import AsyncMock, patch
from uuid import UUID

import asyncclick as click
import pytest

from fragile.commands.interactive.commands.model import ModelCommand, build_model_options, choose_model
from fragile.models import SessionState
from fragile.models.constants import CommandResult
from tomorrow.models.constants import ModelType


class TestModelCommand:
    def test_build_model_options_groups_providers_and_marks_current_model(self) -> None:
        options = build_model_options(
            {
                ModelType.ANTHROPIC: ("claude",),
                ModelType.OPENAI: ("gpt",),
            },
            (ModelType.OPENAI, "gpt"),
        )

        assert options == [
            ((ModelType.ANTHROPIC, "claude"), "Anthropic  claude"),
            ((ModelType.OPENAI, "gpt"), "OpenAI     gpt  Current model"),
        ]

    @pytest.mark.asyncio
    async def test_choose_model_returns_none_for_empty_options(self, capsys) -> None:
        assert await choose_model([]) is None
        assert "No configured models" in capsys.readouterr().out

    @pytest.mark.asyncio
    async def test_choose_model_returns_none_when_cancelled(self) -> None:
        with patch(
            "fragile.commands.interactive.commands.model.select_history",
            new_callable=AsyncMock,
            side_effect=click.Abort(),
        ):
            assert await choose_model([((ModelType.OPENAI, "gpt"), "OpenAI gpt")]) is None

    @pytest.mark.asyncio
    async def test_handle_returns_continue_without_account(self, capsys) -> None:
        with patch(
            "fragile.commands.interactive.commands.model.Account.get_credentials",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await ModelCommand().handle(None, SessionState(thread_id=UUID(int=1)))

        assert result is CommandResult.CONTINUE
        assert "Configure an account" in capsys.readouterr().out

    @pytest.mark.asyncio
    async def test_handle_ignores_cancelled_or_unchanged_selection(self) -> None:
        command = ModelCommand()
        state = SessionState(thread_id=UUID(int=1))
        with (
            patch(
                "fragile.commands.interactive.commands.model.Account.get_credentials",
                new_callable=AsyncMock,
                return_value=("openai", "key", "https://example.com"),
            ),
            patch.object(
                command,
                "_current_selection",
                new_callable=AsyncMock,
                return_value=(ModelType.OPENAI, "gpt-5"),
            ),
            patch(
                "fragile.commands.interactive.commands.model.choose_model",
                new_callable=AsyncMock,
                side_effect=[None, (ModelType.OPENAI, "gpt-5")],
            ),
            patch(
                "fragile.commands.interactive.commands.model.Account.save_model_selection",
                new_callable=AsyncMock,
            ) as save,
        ):
            assert await command.handle(None, state) is CommandResult.CONTINUE
            assert await command.handle(None, state) is CommandResult.CONTINUE

        save.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_handle_persists_changed_selection(self) -> None:
        command = ModelCommand()
        with (
            patch(
                "fragile.commands.interactive.commands.model.Account.get_credentials",
                new_callable=AsyncMock,
                return_value=("openai", "key", "https://example.com"),
            ),
            patch.object(
                command,
                "_current_selection",
                new_callable=AsyncMock,
                return_value=(ModelType.OPENAI, "gpt-4o-mini"),
            ),
            patch(
                "fragile.commands.interactive.commands.model.choose_model",
                new_callable=AsyncMock,
                return_value=(ModelType.OPENAI, "gpt-5"),
            ),
            patch(
                "fragile.commands.interactive.commands.model.Account.save_model_selection",
                new_callable=AsyncMock,
            ) as save,
        ):
            result = await command.handle(None, SessionState(thread_id=UUID(int=1)))

        assert result is CommandResult.MODEL_CHANGED
        save.assert_awaited_once_with(ModelType.OPENAI, "gpt-5")
