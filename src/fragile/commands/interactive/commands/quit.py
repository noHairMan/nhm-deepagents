"""Exit command handling."""

from fragile.models import SessionState
from fragile.models.constants import Command, CommandResult


def is_exit_command(prompt: str) -> bool:
    """Return whether the prompt requests leaving the session."""
    return prompt.strip().casefold() == f"/{Command.QUIT.value}"


def handle_exit(prompt: str, state: SessionState) -> CommandResult:
    """Handle the command that exits the interactive session."""
    del state
    return CommandResult.EXIT if is_exit_command(prompt) else CommandResult.NOT_HANDLED
