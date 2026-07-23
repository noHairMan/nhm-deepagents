from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator
from typing import Any
from uuid import UUID, uuid4

import typer
from langgraph.graph.state import CompiledStateGraph
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

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

_PROMPT_STYLE = Style.from_dict({"prompt": "#00aa00 bold"})
_COMMANDS = ("/new", "/quit")
_console = Console()


class _CommandCompleter(Completer):
    """补全 Fragile 的内置斜杠命令。"""

    def get_completions(self, document: object, complete_event: object) -> Any:
        text_before_cursor = getattr(document, "text_before_cursor", "")
        if not text_before_cursor.startswith("/") or " " in text_before_cursor:
            return
        for command in _COMMANDS:
            if command.startswith(text_before_cursor):
                yield Completion(command, start_position=-len(text_before_cursor))


def _create_prompt_session() -> PromptSession[str]:
    key_bindings = KeyBindings()

    @key_bindings.add("enter")
    def _submit(event: Any) -> None:
        event.current_buffer.validate_and_handle()

    @key_bindings.add("escape", "enter")
    def _insert_newline(event: Any) -> None:
        event.current_buffer.insert_text("\n")

    return PromptSession(
        history=InMemoryHistory(),
        completer=_CommandCompleter(),
        style=_PROMPT_STYLE,
        multiline=True,
        enable_suspend=True,
        key_bindings=key_bindings,
    )


def _prompt(session: PromptSession[str]) -> str:
    """读取一条支持历史、补全和多行编辑的用户输入。"""
    return session.prompt("你> ")


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
    _console.print(Text(_STARTUP_BANNER, style="cyan"), end="")
    if resumed:
        _console.print(Panel(f"已恢复会话  {thread_id}", title="Fragile", border_style="green"))
    else:
        _console.print(
            Panel(
                "Fresh start\nAll previous messages and task state have been cleared\n"
                "Use --thread to continue a previous conversation",
                title="Fragile",
                border_style="yellow",
            )
        )
    _console.print("[bold green]✓ Connected to Tomorrow agent[/bold green]")
    _console.print("[bold cyan]● Fragile is ready.[/bold cyan]\n")


async def _chat(prompt: str, thread_id: UUID) -> None:
    async with get_checkpointer_context() as checkpointer:
        agent = AgentManager.create_agent(checkpointer)
        async for content in _events(agent, prompt, thread_id):
            _console.print(Text(content), end="")
    _console.print()


def interactive(thread: str | None = typer.Option(None, "--thread", "-t", help="用于恢复会话的线程 UUID。")) -> None:
    """启动交互式会话。输入 /quit 退出。"""
    thread_id = _thread_id(thread)
    _enter_fullscreen()
    try:
        _show_startup(thread_id, thread is not None)
        typer.echo("输入 /quit 退出。")
        session = _create_prompt_session()
        last_keyboard_interrupt: float | None = None
        while True:
            try:
                prompt = _prompt(session)
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
