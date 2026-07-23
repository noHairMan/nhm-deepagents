from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any
from uuid import UUID, uuid4

import typer
from langgraph.graph.state import CompiledStateGraph

from fragile.exceptions import InvalidThreadIdError
from tomorrow.conf import settings
from tomorrow.core.agent import AgentManager
from tomorrow.core.checkpoint import get_checkpointer_context


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
    return prompt.strip().casefold() in {"exit", "quit"}


async def _chat(prompt: str, thread_id: UUID) -> None:
    async with get_checkpointer_context() as checkpointer:
        agent = AgentManager.create_agent(checkpointer)
        async for content in _events(agent, prompt, thread_id):
            typer.echo(content, nl=False)
    typer.echo()


def interactive(thread: str | None = typer.Option(None, "--thread", "-t", help="用于恢复会话的线程 UUID。")) -> None:
    """启动交互式会话。输入 exit 或 quit 退出。"""
    thread_id = _thread_id(thread)
    typer.echo("NHM interactive mode，输入 exit 或 quit 退出。")
    while True:
        try:
            prompt = typer.prompt("你")
        except EOFError, KeyboardInterrupt:
            typer.echo()
            break
        if _is_exit_command(prompt):
            break
        if prompt.strip():  # pragma: no branch
            asyncio.run(_chat(prompt, thread_id))
