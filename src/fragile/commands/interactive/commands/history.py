"""History command handling."""

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID

import typer
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.layout import HSplit, Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.utils import get_cwidth
from prompt_toolkit.widgets import Label, RadioList
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from fragile.commands.interactive.commands.base import Command as BaseCommand
from fragile.commands.interactive.display import show_startup
from fragile.models import SessionState
from fragile.models.base import engine, get_initialized_async_session_factory
from fragile.models.constants import CommandResult
from fragile.models.history import ConversationHistory

HISTORY_STYLE = Style.from_dict({"selected-option": "fg:ansigreen bold"})


def select_history(
    message: str,
    options: list[tuple[UUID, str]],
    key_bindings: KeyBindings,
    style: Style,
    symbol: str,
    enable_interrupt: bool,
) -> UUID:
    """Select a history item without displaying option numbers."""
    radio_list = RadioList(
        values=options,
        select_on_focus=True,
        open_character="",
        select_character=symbol,
        close_character="",
        show_cursor=False,
        show_numbers=False,
        container_style="class:input-selection",
        default_style="class:option",
        selected_style="",
        checked_style="class:selected-option",
        number_style="class:number",
        show_scrollbar=False,
    )
    bindings = KeyBindings()

    @bindings.add("enter", eager=True)  # pragma: no cover
    def accept_selection(event: Any) -> None:
        event.app.exit(result=radio_list.current_value)

    if enable_interrupt:  # pragma: no cover

        @bindings.add("c-c", eager=True)  # pragma: no cover
        def interrupt_selection(event: Any) -> None:
            event.app.exit(exception=typer.Abort())

    application = Application(
        layout=Layout(
            HSplit(
                [
                    Label(text=message, dont_extend_height=True),
                    radio_list,
                ]
            ),
            focused_element=radio_list,
        ),
        key_bindings=merge_key_bindings([bindings, key_bindings]),
        style=style,
    )
    return application.run()


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

    async def handle_async(self, prompt: Optional[str], state: SessionState) -> CommandResult:
        """Handle history selection within the active event loop."""
        histories = await list_history()
        selected_thread = choose_history(histories)
        if selected_thread is not None:
            state.thread_id = selected_thread
            show_startup(state.thread_id, True)
        return CommandResult.CONTINUE


async def list_history() -> list[tuple[UUID, str]]:
    """Return conversations with their elapsed update time."""
    if isinstance(engine, Engine):
        with Session(engine) as session:
            conversations = session.scalars(
                select(ConversationHistory).order_by(ConversationHistory.update_time.desc())
            ).all()
    else:
        session_factory = await get_initialized_async_session_factory()
        async with session_factory() as session:
            conversations = (
                await session.scalars(select(ConversationHistory).order_by(ConversationHistory.update_time.desc()))
            ).all()
    titles = [conversation.title for conversation in conversations]
    title_width = max((get_cwidth(title) for title in titles), default=0)
    return [
        (
            UUID(conversation.thread_id),
            format_history_label(
                conversation.title,
                format_elapsed_time(conversation.update_time),
                title_width,
            ),
        )
        for conversation in conversations
    ]


def format_history_label(title: str, elapsed: str, title_width: int) -> str:
    """Format a history item with aligned title and elapsed-time columns."""
    padding = " " * (title_width - get_cwidth(title) + 4)
    return f"{title}{padding}{elapsed}"


def format_elapsed_time(updated_at: datetime, now: datetime | None = None) -> str:
    """Format the time elapsed since a conversation was updated."""
    elapsed = max(timedelta(), (now or datetime.now()) - updated_at)
    seconds = int(elapsed.total_seconds())
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    days = hours // 24
    return f"{days} day{'s' if days != 1 else ''} ago"


def choose_history(
    histories: list[tuple[UUID, str]],
    selector: Callable[..., UUID] | None = None,
) -> UUID | None:
    """Display persisted threads and return the user's selected thread."""
    if not histories:
        typer.echo("No conversation history available.")
        return None
    if selector is None:
        selector = select_history
    key_bindings = KeyBindings()

    @key_bindings.add("escape", eager=True)
    def cancel_selection(event: Any) -> None:
        event.app.exit(exception=typer.Abort())

    try:
        return selector(
            "Select a conversation:",
            options=histories,
            key_bindings=key_bindings,
            style=HISTORY_STYLE,
            symbol="",
            enable_interrupt=False,
        )
    except typer.Abort:
        return None
