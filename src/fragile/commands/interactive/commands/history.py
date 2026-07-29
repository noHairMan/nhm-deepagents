"""History command handling."""

from collections.abc import Callable
from typing import Any, Optional
from uuid import UUID

import typer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import choice
from sqlalchemy import select
from sqlalchemy.orm import Session

from fragile.commands.interactive.commands.base import Command as BaseCommand
from fragile.commands.interactive.display import show_startup
from fragile.models import SessionState
from fragile.models.base import engine
from fragile.models.constants import CommandResult
from fragile.models.history import ConversationHistory


class HistoryCommand(BaseCommand):
    """Select a persisted conversation."""

    name = "history"

    def handle(self, prompt: Optional[str], state: SessionState) -> CommandResult:
        """Handle the history selection command."""
        from asyncio import run

        histories = run(list_history())
        selected_thread = choose_history(histories)
        if selected_thread is not None:
            state.thread_id = selected_thread
            show_startup(state.thread_id, True)
        return CommandResult.CONTINUE


async def list_history() -> list[tuple[UUID, str]]:
    """Return conversations from the persistent title index."""
    with Session(engine) as session:
        conversations = session.scalars(
            select(ConversationHistory).order_by(ConversationHistory.create_time.desc())
        ).all()
    return [(UUID(conversation.thread_id), conversation.title) for conversation in conversations]


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
