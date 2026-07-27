"""Commands available in the interactive session."""

from collections.abc import Callable

from fragile.commands.interactive.commands.base import CommandResult, SessionState
from fragile.commands.interactive.commands.history import handle_history
from fragile.commands.interactive.commands.new import handle_new
from fragile.commands.interactive.commands.quit import handle_exit

CommandHandler = Callable[[str, SessionState], CommandResult]
COMMAND_HANDLERS: tuple[CommandHandler, ...] = (handle_exit, handle_new, handle_history)


def handle_command(prompt: str, state: SessionState) -> CommandResult:
    """Dispatch a prompt to the first registered matching command handler."""
    for handler in COMMAND_HANDLERS:
        result = handler(prompt, state)
        if result is not CommandResult.NOT_HANDLED:
            return result
    return CommandResult.NOT_HANDLED
