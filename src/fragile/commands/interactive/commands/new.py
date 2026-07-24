"""New conversation command handling."""

from fragile.enums import Command


def is_new_command(prompt: str) -> bool:
    """Return whether the prompt requests a new conversation."""
    return prompt.strip().casefold() == f"/{Command.NEW.value}"
