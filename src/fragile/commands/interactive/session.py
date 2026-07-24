"""Interactive session orchestration."""

import asyncio
import time
from uuid import UUID, uuid4

import typer

from fragile.commands.interactive.agent import chat
from fragile.commands.interactive.commands.history import (
    choose_history as _choose_history,
)
from fragile.commands.interactive.commands.history import (
    is_history_command,
)
from fragile.commands.interactive.commands.history import (
    list_thread_ids as _list_thread_ids,
)
from fragile.commands.interactive.commands.new import is_new_command
from fragile.commands.interactive.commands.quit import is_exit_command
from fragile.commands.interactive.display import (
    enter_fullscreen,
    leave_fullscreen,
    print_stream,
    show_startup,
)
from fragile.commands.interactive.input import create_prompt_session, prompt
from fragile.exceptions import InvalidThreadIdError
from tomorrow.core.checkpoint import get_checkpointer_context


def parse_thread_id(value: str | None) -> UUID:
    if value is None:
        return uuid4()
    try:
        return UUID(value)
    except ValueError as error:
        raise InvalidThreadIdError("必须是有效的 UUID") from error


def choose_history(prompt_session: object, thread_ids: list[UUID]) -> UUID | None:
    """Display persisted threads and return the user's selected thread."""
    return _choose_history(prompt_session, thread_ids, prompt)


async def list_thread_ids() -> list[UUID]:
    """Return the distinct persisted conversation thread IDs."""
    return await _list_thread_ids(get_checkpointer_context)  # pragma: no branch


def interactive(
    thread: str | None = typer.Option(None, "--thread", "-t", help="用于恢复会话的线程 UUID。"),
) -> None:
    """启动交互式会话。输入 /quit 退出。"""
    thread_id = parse_thread_id(thread)
    enter_fullscreen()
    try:
        show_startup(thread_id, thread is not None)
        prompt_session = create_prompt_session()
        last_keyboard_interrupt: float | None = None
        while True:
            try:
                input_prompt = prompt(prompt_session)
            except KeyboardInterrupt, typer.Abort:
                typer.echo()
                now = time.monotonic()
                if last_keyboard_interrupt is not None and now - last_keyboard_interrupt <= 1:
                    break
                last_keyboard_interrupt = now
                continue
            except EOFError:
                continue
            last_keyboard_interrupt = None
            if is_exit_command(input_prompt):
                break
            if is_new_command(input_prompt):
                thread_id = uuid4()
                show_startup(thread_id, False)
                continue
            if is_history_command(input_prompt):
                thread_ids = asyncio.run(list_thread_ids())
                selected_thread = choose_history(prompt_session, thread_ids)
                if selected_thread is not None:
                    thread_id = selected_thread
                    show_startup(thread_id, True)
                continue
            if input_prompt.strip():
                asyncio.run(chat(input_prompt, thread_id, print_stream))
    finally:
        leave_fullscreen()
