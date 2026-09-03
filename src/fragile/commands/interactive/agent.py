"""Tomorrow Agent communication handling."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from importlib import import_module
from typing import Any
from uuid import UUID

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph

from fragile.commands.interactive.display import TimelineRenderer
from fragile.commands.interactive.trace import (
    StreamSegment,
    TraceEvent,
    content_segments,
    content_text,
    normalize_event,
    trace_to_json,
)
from fragile.conf import settings as fragile_settings
from fragile.exceptions import AgentFactoryImportError, AgentFactoryTypeError, AgentGraphTypeError, AgentResponseError
from fragile.models import SessionOutput, restore_account_configuration
from tomorrow.conf import settings
from tomorrow.core.checkpoint import get_checkpointer_context

__all__ = ["StreamSegment", "TraceEvent", "content_segments", "content_text", "stream_events"]


async def stream_events(agent: CompiledStateGraph, prompt: str, thread_id: UUID) -> AsyncIterator[TraceEvent]:
    """Yield normalized LangGraph events while preserving stream order."""
    sequence = 0
    try:
        async for event in agent.astream_events(
            {"messages": [("user", prompt)]},
            config={"recursion_limit": settings.RECURSION_LIMIT, "configurable": {"thread_id": thread_id}},
            version="v2",
        ):
            normalized = normalize_event(event, sequence)
            for trace_event in normalized:
                yield trace_event
                sequence = max(sequence, trace_event.sequence + 1)
    except ValueError as error:
        raise AgentResponseError(str(error)) from error


def load_agent_factory(path: str) -> Any:
    """Load an agent factory from its dotted import path."""
    try:
        parts = path.split(".")
        for index in range(len(parts) - 1, 0, -1):
            try:
                factory: Any = import_module(".".join(parts[:index]))
                for attribute in parts[index:]:
                    factory = getattr(factory, attribute)
                break
            except ImportError:
                continue
        else:
            raise ImportError(path)
    except (ImportError, AttributeError, ValueError) as error:
        raise AgentFactoryImportError(f"Unable to load configured agent factory '{path}'.") from error
    if not callable(factory):
        raise AgentFactoryTypeError(f"Configured agent factory '{path}' is not callable.")
    return factory


def create_agent(checkpointer: BaseCheckpointSaver | None = None) -> CompiledStateGraph:
    """Create the configured agent and validate its graph contract."""
    factory = load_agent_factory(fragile_settings.AGENT)
    agent = factory(checkpointer)
    if not isinstance(agent, CompiledStateGraph):
        raise AgentGraphTypeError(
            f"Configured agent factory '{fragile_settings.AGENT}' did not return a CompiledStateGraph."
        )
    return agent


@asynccontextmanager
async def agent_runtime() -> AsyncIterator[tuple[CompiledStateGraph, BaseCheckpointSaver | None]]:
    """Create an agent and its checkpointer for one interactive session."""
    async with get_checkpointer_context() as checkpointer:
        await restore_account_configuration()
        yield create_agent(checkpointer), checkpointer


async def chat(agent: CompiledStateGraph, prompt: str, thread_id: UUID) -> None:
    contents: list[str] = []
    thinking_contents: list[str] = []
    trace_events: list[TraceEvent] = []
    renderer = TimelineRenderer()
    async for event in stream_events(agent, prompt, thread_id):
        trace_events.append(event)
        renderer.render(event)
        if event.kind == "thinking":
            thinking_contents.append(event.content or "")
        elif event.kind == "text":
            contents.append(event.content or "")
    renderer.finish()
    complete_output = "".join(contents)
    thinking_output = "".join(thinking_contents)
    await SessionOutput.save_output(
        thread_id,
        prompt,
        complete_output,
        complete_output,
        thinking_output=thinking_output or None,
        trace_payload=trace_to_json(trace_events),
    )
