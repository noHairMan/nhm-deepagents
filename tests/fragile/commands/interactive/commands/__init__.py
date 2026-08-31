"""Tests for interactive session commands."""

from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest

from fragile.commands.interactive.commands import (
    CommandRegistry,
    create_command_registry,
    load_command,
)
from fragile.commands.interactive.commands.base import Command
from fragile.exceptions import InvalidCommandError
from fragile.models import SessionState
from fragile.models.constants import CommandResult


class StubCommand(Command):
    name = "stub"

    async def handle(self, prompt: str | None, state: SessionState) -> CommandResult:
        return CommandResult.CONTINUE


class TestCommandRegistry:
    def test_register_rejects_non_command(self) -> None:
        registry = CommandRegistry()

        with pytest.raises(InvalidCommandError):
            registry.register(object())

    def test_handlers_returns_registered_commands(self) -> None:
        registry = CommandRegistry()
        command = StubCommand()
        registry.register(command)

        assert registry.handlers == (command,)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("prompt", ["hello", "/missing hello"])
    async def test_handle_returns_not_handled_for_unknown_prompt(self, prompt: str) -> None:
        registry = CommandRegistry()
        registry.register(StubCommand())

        assert await registry.handle(prompt, SessionState(thread_id=UUID(int=1))) is CommandResult.NOT_HANDLED

    @pytest.mark.asyncio
    async def test_handle_dispatches_normalized_command(self) -> None:
        registry = CommandRegistry()
        command = StubCommand()
        command.handle = AsyncMock(return_value=CommandResult.CONTINUE)
        registry.register(command)
        state = SessionState(thread_id=UUID(int=1))

        result = await registry.handle("  /STUB prompt  ", state)

        assert result is CommandResult.CONTINUE
        command.handle.assert_awaited_once_with("prompt", state)


class TestCommandLoading:
    def test_load_command_imports_and_instantiates_class(self) -> None:
        command = load_command("fragile.commands.interactive.commands.new.NewCommand")

        assert command.name == "new"

    def test_load_command_imports_model_command(self) -> None:
        command = load_command("fragile.commands.interactive.commands.model.ModelCommand")

        assert command.name == "model"

    def test_create_command_registry_uses_enabled_commands(self) -> None:
        with patch(
            "fragile.commands.interactive.commands.settings.ENABLED_COMMANDS",
            ("fragile.commands.interactive.commands.new.NewCommand",),
        ):
            registry = create_command_registry()

        assert tuple(command.name for command in registry.handlers) == ("new",)
