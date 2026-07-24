"""History command handling."""

from collections.abc import Callable
from uuid import UUID

import typer

from fragile.enums import Command
from tomorrow.core.checkpoint import get_checkpointer_context


def is_history_command(prompt: str) -> bool:
    """Return whether the prompt requests conversation history."""
    return prompt.strip().casefold() == f"/{Command.HISTORY.value}"


async def list_thread_ids(checkpointer_context: Callable[[], object] = get_checkpointer_context) -> list[UUID]:
    """Return the distinct persisted conversation thread IDs."""
    thread_ids: set[UUID] = set()
    async with checkpointer_context() as checkpointer:  # pragma: no branch
        if checkpointer is None:
            return []
        async for checkpoint in checkpointer.alist(None):
            value = checkpoint.config.get("configurable", {}).get("thread_id")
            if value is not None:
                thread_ids.add(UUID(str(value)))
    return sorted(thread_ids, key=str)


def choose_history(
    prompt_session: object,
    thread_ids: list[UUID],
    prompt: Callable[[object], str],
) -> UUID | None:
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
