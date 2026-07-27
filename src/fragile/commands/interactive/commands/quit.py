"""Exit command handling."""

from fragile.commands.interactive.commands.base import CommandResult, SessionState
from fragile.enums import Command


def is_exit_command(prompt: str) -> bool:
    """Return whether the prompt requests leaving the session."""
    return prompt.strip().casefold() == f"/{Command.QUIT.value}"


def handle_exit(prompt: str, state: SessionState) -> CommandResult:
    """Handle the command that exits the interactive session."""
    del state
    return CommandResult.EXIT if is_exit_command(prompt) else CommandResult.NOT_HANDLED
