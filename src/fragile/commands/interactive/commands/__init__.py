"""Commands available in the interactive session."""

from importlib import import_module

from fragile.commands.interactive.commands.base import Command, extract_prompt
from fragile.conf import settings
from fragile.exceptions import InvalidCommandError
from fragile.models import SessionState
from fragile.models.constants import CommandResult


class CommandRegistry:
    """Register and dispatch interactive commands by their normalized name."""

    def __init__(self) -> None:
        self._handlers: dict[str, Command] = {}

    def register(self, command: Command) -> None:
        """Register a command instance."""
        if not isinstance(command, Command):
            raise InvalidCommandError("command must be a Command instance")
        self._handlers[command.name] = command

    @property
    def handlers(self) -> tuple[Command]:
        """Return the registered commands."""
        return tuple(self._handlers.values())

    def is_registered(self, prompt: str) -> bool:
        """Return whether a prompt addresses a registered command."""
        parsed_prompt = extract_prompt(prompt)
        return parsed_prompt.command in self._handlers

    def clears_output_after_handling(self, prompt: str) -> bool:
        """Return whether handling a prompt may leave a nested screen behind."""
        parsed_prompt = extract_prompt(prompt)
        handler = self._handlers.get(parsed_prompt.command)
        return handler is not None and handler.clears_output_after_handling

    async def handle(self, prompt: str, state: SessionState) -> CommandResult:
        """Dispatch a prompt without blocking the active event loop."""
        parsed_prompt = extract_prompt(prompt)
        if parsed_prompt.command is None:
            return CommandResult.NOT_HANDLED
        handler = self._handlers.get(parsed_prompt.command)
        if handler is None:
            return CommandResult.NOT_HANDLED
        return await handler.handle(parsed_prompt.prompt, state)


def load_command(path: str) -> Command:
    """Dynamically import and instantiate a command class."""
    module_name, class_name = path.rsplit(".", 1)
    command_class = getattr(import_module(module_name), class_name)
    return command_class()


def create_command_registry() -> CommandRegistry:
    registry = CommandRegistry()
    for path in settings.ENABLED_COMMANDS:
        registry.register(load_command(path))
    return registry


command_registry = create_command_registry()
