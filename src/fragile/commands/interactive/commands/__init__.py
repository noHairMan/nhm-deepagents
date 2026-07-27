"""Commands available in the interactive session."""

from collections.abc import Callable
from importlib import import_module

from fragile.commands.interactive.commands.base import Command
from fragile.commands.interactive.commands.history import handle_history
from fragile.commands.interactive.commands.new import handle_new
from fragile.commands.interactive.commands.quit import handle_exit
from fragile.models import SessionState
from fragile.models.constants import CommandResult
from fragile.settings import FragileSettings

type LegacyHandler = Callable[[str, SessionState], CommandResult]
type CommandHandler = Command | LegacyHandler


class CommandRegistry:
    """Register and dispatch interactive commands by their normalized name."""

    def __init__(self) -> None:
        self._handlers: dict[str, CommandHandler] = {}

    def register(self, command: CommandHandler, handler: LegacyHandler | None = None) -> None:
        """Register a command instance."""
        if handler is not None:
            self._handlers[f"/{str(command).strip().lstrip('/').casefold()}"] = handler
            return
        if not isinstance(command, Command):
            raise TypeError("command must be a Command instance")
        self._handlers[f"/{command.name.strip().lstrip('/').casefold()}"] = command

    def build(self, enabled_commands: tuple[str, ...]) -> dict[str, CommandHandler]:
        """Return the enabled command handlers as a direct lookup map."""
        enabled = {name.strip() for name in enabled_commands}
        return {
            key: command
            for key, command in self._handlers.items()
            if isinstance(command, Command)
            and command.__class__.__module__ + "." + command.__class__.__name__ in enabled
            or not isinstance(command, Command)
            and key[1:] in enabled
        }


def _load_command(path: str) -> CommandHandler:
    """Dynamically import and instantiate a command class."""
    module_name, class_name = path.rsplit(".", 1)
    command_class = getattr(import_module(module_name), class_name)
    return command_class()


def _create_command_map() -> dict[str, CommandHandler]:
    registry = CommandRegistry()
    settings = FragileSettings()
    for path in settings.ENABLED_COMMANDS:
        registry.register(_load_command(path))
    return registry.build(settings.ENABLED_COMMANDS)


COMMAND_HANDLER_MAP: dict[str, CommandHandler] = _create_command_map()


def handle_command(prompt: str, state: SessionState) -> CommandResult:
    """Dispatch a prompt to its registered command handler in constant time."""
    handler = COMMAND_HANDLER_MAP.get(prompt.strip().casefold())
    if handler is None:
        return CommandResult.NOT_HANDLED
    return handler.handle(prompt, state) if isinstance(handler, Command) else handler(prompt, state)
