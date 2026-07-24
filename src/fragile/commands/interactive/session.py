"""Interactive session orchestration."""

import asyncio
import time
from uuid import UUID, uuid4

import typer

from fragile.commands.interactive.agent import chat
from fragile.commands.interactive.display import (
    enter_fullscreen,
    leave_fullscreen,
    print_stream,
    show_startup,
)
from fragile.commands.interactive.input import create_prompt_session, prompt
from fragile.enums import Command
from fragile.exceptions import InvalidThreadIdError
from tomorrow.core.checkpoint import get_checkpointer_context


def parse_thread_id(value: str | None) -> UUID:
    if value is None:
        return uuid4()
    try:
        return UUID(value)
    except ValueError as error:
        raise InvalidThreadIdError("必须是有效的 UUID") from error


def is_exit_command(prompt: str) -> bool:
    return prompt.strip().casefold() == f"/{Command.QUIT.value}"


def is_new_command(prompt: str) -> bool:
    return prompt.strip().casefold() == f"/{Command.NEW.value}"


def is_history_command(prompt: str) -> bool:
    return prompt.strip().casefold() == f"/{Command.HISTORY.value}"


async def list_thread_ids() -> list[UUID]:
    """Return the distinct persisted conversation thread IDs."""
    thread_ids: set[UUID] = set()
    async with get_checkpointer_context() as checkpointer:
        if checkpointer is None:
            return []
        async for checkpoint in checkpointer.alist(None):
            value = checkpoint.config.get("configurable", {}).get("thread_id")
            if value is not None:
                thread_ids.add(UUID(str(value)))
    return sorted(thread_ids, key=str)


def choose_history(prompt_session: object, thread_ids: list[UUID]) -> UUID | None:
    """Display persisted threads and return the user's selected thread."""
    if not thread_ids:
        typer.echo("暂无历史会话")
        return None
    typer.echo("历史会话：")
    for index, thread_id in enumerate(thread_ids, 1):
        typer.echo(f"{index}. {thread_id}")
    value = prompt(prompt_session).strip()
    if value.isdigit() and 1 <= int(value) <= len(thread_ids):
        return thread_ids[int(value) - 1]
    try:
        selected = UUID(value)
    except ValueError:
        typer.echo("无效的会话编号或 UUID")
        return None
    if selected not in thread_ids:
        typer.echo("找不到该历史会话")
        return None
    return selected


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
