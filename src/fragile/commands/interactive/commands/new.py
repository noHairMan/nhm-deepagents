"""New conversation command handling."""

from uuid import uuid4

from fragile.commands.interactive.display import show_startup
from fragile.models import SessionState
from fragile.models.constants import Command, CommandResult


def is_new_command(prompt: str) -> bool:
    """Return whether the prompt requests a new conversation."""
    return prompt.strip().casefold() == f"/{Command.NEW.value}"


def handle_new(prompt: str, state: SessionState) -> CommandResult:
    """Handle the command that starts a new conversation."""
    if not is_new_command(prompt):
        return CommandResult.NOT_HANDLED
    state.thread_id = uuid4()
    show_startup(state.thread_id, False)
    return CommandResult.CONTINUE
