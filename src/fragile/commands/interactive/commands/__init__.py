"""Commands available in the interactive session."""

from importlib import import_module

from fragile.commands.interactive.commands.base import Command, extract_prompt
from fragile.conf import settings
from fragile.models import SessionState
from fragile.models.constants import CommandResult


class CommandRegistry:
    """Register and dispatch interactive commands by their normalized name."""

    def __init__(self) -> None:
        self._handlers: dict[str, Command] = {}

    def register(self, command: Command) -> None:
        """Register a command instance."""
        if not isinstance(command, Command):
            raise TypeError("command must be a Command instance")
        self._handlers[command.name] = command

    def handle(self, prompt: str, state: SessionState) -> CommandResult:
        """Dispatch a prompt to its registered command handler in constant time."""
        parsed_prompt = extract_prompt(prompt)
        if parsed_prompt.command is None:
            return CommandResult.NOT_HANDLED
        handler = self._handlers.get(parsed_prompt.command)
        if handler is None:
            return CommandResult.NOT_HANDLED
        return handler.handle(parsed_prompt.prompt, state)


def _load_command(path: str) -> Command:
    """Dynamically import and instantiate a command class."""
    module_name, class_name = path.rsplit(".", 1)
    command_class = getattr(import_module(module_name), class_name)
    return command_class()


def _create_command_registry() -> CommandRegistry:
    registry = CommandRegistry()
    for path in settings.ENABLED_COMMANDS:
        registry.register(_load_command(path))
    return registry


COMMAND_REGISTRY = _create_command_registry()
