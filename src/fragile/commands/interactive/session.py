"""Interactive session orchestration."""

import asyncio
import time
from uuid import UUID, uuid4

import typer

from fragile.commands.interactive.agent import chat
from fragile.commands.interactive.commands import COMMAND_REGISTRY
from fragile.commands.interactive.display import (
    enter_fullscreen,
    leave_fullscreen,
    print_stream,
    show_startup,
)
from fragile.commands.interactive.input import create_prompt_session, prompt
from fragile.commands.interactive.input import prompt_async as _prompt_async
from fragile.conf import settings
from fragile.exceptions import InvalidThreadIdError
from fragile.models import ConversationHistory, SessionState
from fragile.models.constants import CommandResult

_sync_prompt = prompt


def parse_thread_id(value: str | None) -> UUID:
    if value is None:
        return uuid4()
    try:
        return UUID(value)
    except ValueError as error:
        raise InvalidThreadIdError("Must be a valid UUID") from error


async def interactive_async(
    thread: str | None = typer.Option(None, "--thread", "-t", help="Thread UUID to resume a conversation."),
) -> None:
    """Start an interactive session. Enter /quit to exit."""
    thread_id = parse_thread_id(thread)
    enter_fullscreen()
    try:
        show_startup(thread_id, thread is not None)
        prompt_session = create_prompt_session()
        state = SessionState(thread_id=thread_id, prompt_session=prompt_session)
        last_keyboard_interrupt: float | None = None
        while True:
            try:
                if prompt is _sync_prompt:
                    input_prompt = await _prompt_async(prompt_session)
                else:
                    input_prompt = prompt(prompt_session)
            except KeyboardInterrupt, typer.Abort:
                typer.echo()
                now = time.monotonic()
                if (
                    last_keyboard_interrupt is not None
                    and now - last_keyboard_interrupt <= settings.INTERRUPT_EXIT_THRESHOLD
                ):
                    break
                last_keyboard_interrupt = now
                continue
            except EOFError:
                continue
            last_keyboard_interrupt = None
            result = await COMMAND_REGISTRY.handle_async(input_prompt, state)
            if result is CommandResult.EXIT:
                break
            if result is CommandResult.CONTINUE:
                continue
            if input_prompt.strip():
                await ConversationHistory.register_conversation_async(state.thread_id, input_prompt)
                await chat(input_prompt, state.thread_id, print_stream)
    finally:
        leave_fullscreen()


def interactive(
    thread: str | None = typer.Option(None, "--thread", "-t", help="Thread UUID to resume a conversation."),
) -> None:
    """Start an interactive session through the legacy synchronous boundary."""
    thread_id = parse_thread_id(thread)
    enter_fullscreen()
    try:
        show_startup(thread_id, thread is not None)
        prompt_session = create_prompt_session()
        state = SessionState(thread_id=thread_id, prompt_session=prompt_session)
        last_keyboard_interrupt: float | None = None
        while True:
            try:
                input_prompt = prompt(prompt_session)
            except KeyboardInterrupt, typer.Abort:
                typer.echo()
                now = time.monotonic()
                if (
                    last_keyboard_interrupt is not None
                    and now - last_keyboard_interrupt <= settings.INTERRUPT_EXIT_THRESHOLD
                ):
                    break
                last_keyboard_interrupt = now
                continue
            except EOFError:
                continue
            last_keyboard_interrupt = None
            result = COMMAND_REGISTRY.handle(input_prompt, state)
            if result is CommandResult.EXIT:
                break
            if result is CommandResult.CONTINUE:
                continue
            if input_prompt.strip():
                ConversationHistory.register_conversation(state.thread_id, input_prompt)
                asyncio.run(chat(input_prompt, state.thread_id, print_stream))
    finally:
        leave_fullscreen()
