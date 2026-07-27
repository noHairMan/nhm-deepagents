"""Commands available in the interactive session."""

from importlib import import_module

from fragile.commands.interactive.commands.base import Command
from fragile.models import SessionState
from fragile.models.constants import CommandResult
from fragile.settings import FragileSettings


class CommandRegistry:
    """Register and dispatch interactive commands by their normalized name."""

    def __init__(self) -> None:
        self._handlers: dict[str, Command] = {}

    def register(self, command: Command) -> None:
        """Register a command instance."""
        if not isinstance(command, Command):
            raise TypeError("command must be a Command instance")
        self._handlers[f"/{command.name.strip().lstrip('/').casefold()}"] = command

    def build(self, enabled_commands: tuple[str, ...]) -> dict[str, Command]:
        """Return the enabled command handlers as a direct lookup map."""
        enabled = {name.strip() for name in enabled_commands}
        return {
            key: command
            for key, command in self._handlers.items()
            if command.__class__.__module__ + "." + command.__class__.__name__ in enabled
        }

    def handle(self, prompt: str, state: SessionState) -> CommandResult:
        """Dispatch a prompt to its registered command handler in constant time."""
        handler = self._handlers.get(prompt.strip().casefold())
        if handler is None:
            return CommandResult.NOT_HANDLED
        return handler.handle(prompt, state)


def _load_command(path: str) -> Command:
    """Dynamically import and instantiate a command class."""
    module_name, class_name = path.rsplit(".", 1)
    command_class = getattr(import_module(module_name), class_name)
    return command_class()


def _create_command_registry() -> CommandRegistry:
    registry = CommandRegistry()
    settings = FragileSettings()
    for path in settings.ENABLED_COMMANDS:
        registry.register(_load_command(path))
    registry._handlers = registry.build(settings.ENABLED_COMMANDS)
    return registry


COMMAND_REGISTRY = _create_command_registry()
