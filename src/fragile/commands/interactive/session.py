"""Interactive session orchestration."""

import time
from uuid import UUID, uuid4

import asyncclick as click

from fragile.commands.interactive.agent import chat
from fragile.commands.interactive.commands import command_registry
from fragile.commands.interactive.display import (
    enter_fullscreen,
    leave_fullscreen,
    show_startup,
)
from fragile.commands.interactive.input import create_prompt_session
from fragile.conf import settings
from fragile.exceptions import InvalidThreadIdError
from fragile.models import ConversationHistory, SessionState
from fragile.models.constants import CommandResult


def parse_thread_id(value: str | None) -> UUID:
    if value is None:
        return uuid4()
    try:
        return UUID(value)
    except ValueError as error:
        raise InvalidThreadIdError("Must be a valid UUID") from error


async def interactive(
    thread: str | None,
) -> None:
    """Start an interactive session. Enter /quit to exit."""
    thread_id = parse_thread_id(thread)
    enter_fullscreen()
    try:
        show_startup(thread_id, thread is not None)
        session = create_prompt_session()
        state = SessionState(thread_id=thread_id)
        last_keyboard_interrupt: float | None = None
        while True:
            try:
                user_input = await session.prompt_async("> ")
            except KeyboardInterrupt, EOFError, click.Abort:
                click.echo()
                now = time.monotonic()
                if (
                    last_keyboard_interrupt is not None
                    and now - last_keyboard_interrupt <= settings.INTERRUPT_EXIT_THRESHOLD
                ):
                    return
                last_keyboard_interrupt = now
                continue

            last_keyboard_interrupt = None
            user_input = user_input.strip()

            result = await command_registry.handle(user_input, state)
            if result is CommandResult.EXIT:
                return
            if result is CommandResult.CONTINUE:
                continue
            if not user_input:
                continue

            await ConversationHistory.register_conversation(state.thread_id, user_input)
            await chat(user_input, state.thread_id)
    finally:
        leave_fullscreen()
