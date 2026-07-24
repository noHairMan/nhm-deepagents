"""Exit command handling."""

from fragile.enums import Command


def is_exit_command(prompt: str) -> bool:
    """Return whether the prompt requests leaving the session."""
    return prompt.strip().casefold() == f"/{Command.QUIT.value}"
