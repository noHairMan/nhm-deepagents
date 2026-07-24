"""Interactive session orchestration."""

import asyncio
import time
from uuid import UUID, uuid4

import typer

from fragile.commands.interactive.agent import chat
from fragile.commands.interactive.display import (
    clear_screen,
    enter_fullscreen,
    leave_fullscreen,
    print_stream,
    show_startup,
)
from fragile.commands.interactive.input import create_prompt_session, prompt
from fragile.enums import Command
from fragile.exceptions import InvalidThreadIdError


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
                clear_screen()
                thread_id = uuid4()
                show_startup(thread_id, False)
                continue
            if input_prompt.strip():
                asyncio.run(chat(input_prompt, thread_id, print_stream))
    finally:
        leave_fullscreen()
