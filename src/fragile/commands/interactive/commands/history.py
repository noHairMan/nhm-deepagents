"""History command handling."""

from collections.abc import Callable
from typing import Any
from uuid import UUID

import typer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice

from fragile.commands.interactive.commands.base import CommandResult, SessionState
from fragile.commands.interactive.display import show_startup
from fragile.enums import Command
from tomorrow.core.checkpoint import get_checkpointer_context


def is_history_command(prompt: str) -> bool:
    """Return whether the prompt requests conversation history."""
    return prompt.strip().casefold() == f"/{Command.HISTORY.value}"


def _message_title(message: Any) -> str | None:  # pragma: no cover - defensive format compatibility
    """Extract a user message's content from checkpoint data."""
    if isinstance(message, list):
        for nested in message:
            title = _message_title(nested)
            if title is not None:
                return title
        return None
    message_type = (
        message.type if hasattr(message, "type") else message.get("type") if isinstance(message, dict) else None
    )
    if message_type not in {"human", "user"}:
        return None
    content = message.content if hasattr(message, "content") else message.get("content", "")
    return str(content)


async def list_history(
    checkpointer_context: Callable[[], object] = get_checkpointer_context,
) -> list[tuple[UUID, str]]:
    """Return distinct persisted threads with their conversation titles."""
    histories: dict[UUID, str] = {}
    async with checkpointer_context() as checkpointer:  # pragma: no branch
        if checkpointer is None:  # pragma: no cover - unavailable persistence backend
            return []
        async for checkpoint in checkpointer.alist(None):
            config = checkpoint.config.get("configurable", {})
            value = config.get("thread_id")
            if value is None:  # pragma: no cover - malformed checkpoint compatibility
                continue
            thread_id = UUID(str(value))
            checkpoint_data: dict[str, Any] = checkpoint.checkpoint
            messages = checkpoint_data.get("channel_values", {}).get("messages", [])
            title = next(
                (title for message in messages if (title := _message_title(message)) is not None),
                "Untitled conversation",  # pragma: no cover - malformed checkpoint compatibility
            )
            histories[thread_id] = title
    return sorted(histories.items(), key=lambda item: str(item[0]))


def choose_history(
    histories: list[tuple[UUID, str]],
    selector: Callable[..., UUID] | None = None,
) -> UUID | None:
    """Display persisted threads and return the user's selected thread."""
    if not histories:
        typer.echo("No conversation history available.")
        return None
    if selector is None:
        selector = choice
    key_bindings = KeyBindings()

    @key_bindings.add("escape", eager=True)
    def cancel_selection(event: Any) -> None:
        event.app.exit(exception=typer.Abort())

    try:
        return selector(
            "Select a conversation:",
            options=histories,
            key_bindings=key_bindings,
            enable_interrupt=False,
        )
    except typer.Abort:
        return None


def handle_history(prompt_value: str, state: SessionState) -> CommandResult:
    """Handle the command that selects a persisted conversation."""
    if not is_history_command(prompt_value):
        return CommandResult.NOT_HANDLED
    from asyncio import run

    histories = run(list_history())
    selected_thread = choose_history(histories)
    if selected_thread is not None:
        state.thread_id = selected_thread
        show_startup(state.thread_id, True)
    return CommandResult.CONTINUE
