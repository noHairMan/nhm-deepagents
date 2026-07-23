from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator
from typing import Any
from uuid import UUID, uuid4

import typer
from langgraph.graph.state import CompiledStateGraph

from fragile.exceptions import InvalidThreadIdError
from tomorrow.conf import settings
from tomorrow.core.agent import AgentManager
from tomorrow.core.checkpoint import get_checkpointer_context

_STARTUP_BANNER = """\
  ███████╗██████╗  █████╗  ██████╗ ██╗██╗     ███████╗
  ██╔════╝██╔══██╗██╔══██╗██╔════╝ ██║██║     ██╔════╝
  █████╗  ██████╔╝███████║██║  ███╗██║██║     █████╗
  ██╔══╝  ██╔══██╗██╔══██║██║   ██║██║██║     ██╔══╝
  ██║     ██║  ██║██║  ██║╚██████╔╝██║███████╗███████╗
  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝╚══════╝╚══════╝
"""


def _thread_id(value: str | None) -> UUID:
    if value is None:
        return uuid4()
    try:
        return UUID(value)
    except ValueError as error:
        raise InvalidThreadIdError("必须是有效的 UUID") from error


async def _events(agent: CompiledStateGraph, prompt: str, thread_id: UUID) -> AsyncIterator[str]:
    async for event in agent.astream_events(
        {"messages": [("user", prompt)]},
        config={"recursion_limit": settings.RECURSION_LIMIT, "configurable": {"thread_id": thread_id}},
        version="v2",
    ):
        if not isinstance(event, dict) or event.get("event") != "on_chat_model_stream":
            continue
        chunk = event.get("data", {}).get("chunk")
        content = _content_text(getattr(chunk, "content", ""))
        if content:
            yield content


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and isinstance(block.get("text"), str):
            parts.append(block["text"])
    return "".join(parts)


def _is_exit_command(prompt: str) -> bool:
    return prompt.strip().casefold() == "/quit"


def _is_new_command(prompt: str) -> bool:
    return prompt.strip().casefold() == "/new"


def _clear_screen() -> None:
    typer.echo("\033[2J\033[3J\033[H", nl=False, color=True)


def _enter_fullscreen() -> None:
    typer.echo("\033[2J\033[3J\033[H\033[?25l", nl=False, color=True)


def _leave_fullscreen() -> None:
    typer.echo("\033[?25h", nl=False, color=True)


def _show_startup(thread_id: UUID, resumed: bool) -> None:
    """显示交互式会话的启动信息。"""
    typer.echo(_STARTUP_BANNER)
    if resumed:
        typer.echo(f"  已恢复会话  {thread_id}")
    else:
        typer.echo("  Fresh start")
        typer.echo("  All previous messages and task state have been cleared")
        typer.echo("  Use --thread to continue a previous conversation")
    typer.echo("\n  ✓ Connected to Tomorrow agent")
    typer.echo("  ● Fragile is ready.\n")


async def _chat(prompt: str, thread_id: UUID) -> None:
    async with get_checkpointer_context() as checkpointer:
        agent = AgentManager.create_agent(checkpointer)
        async for content in _events(agent, prompt, thread_id):
            typer.echo(content, nl=False)
    typer.echo()


def interactive(thread: str | None = typer.Option(None, "--thread", "-t", help="用于恢复会话的线程 UUID。")) -> None:
    """启动交互式会话。输入 /quit 退出。"""
    thread_id = _thread_id(thread)
    _enter_fullscreen()
    try:
        _show_startup(thread_id, thread is not None)
        typer.echo("输入 /quit 退出。")
        last_keyboard_interrupt: float | None = None
        while True:
            try:
                prompt = typer.prompt("你")
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
            if _is_exit_command(prompt):
                break
            if _is_new_command(prompt):
                _clear_screen()
                thread_id = uuid4()
                _show_startup(thread_id, False)
                continue
            if prompt.strip():  # pragma: no branch
                asyncio.run(_chat(prompt, thread_id))
    finally:
        _leave_fullscreen()
