"""Tomorrow Agent communication handling."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from importlib import import_module
from typing import Any, Literal
from uuid import UUID

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph

from fragile.commands.interactive.display import print_stream, print_thinking
from fragile.conf import settings as fragile_settings
from fragile.exceptions import AgentFactoryImportError, AgentFactoryTypeError, AgentGraphTypeError, AgentResponseError
from fragile.models import SessionOutput, restore_account_configuration
from tomorrow.conf import settings
from tomorrow.core.checkpoint import get_checkpointer_context


@dataclass(frozen=True)
class StreamSegment:
    kind: Literal["thinking", "text"]
    content: str


def content_segments(content: Any) -> list[StreamSegment]:
    if isinstance(content, str):
        return [StreamSegment("text", content)] if content else []
    if not isinstance(content, list):
        return []

    segments: list[StreamSegment] = []
    for block in content:
        if isinstance(block, str):
            if block:
                segments.append(StreamSegment("text", block))
            continue
        if not isinstance(block, dict):
            continue

        block_type = block.get("type")
        if block_type == "reasoning" or "reasoning" in block:
            reasoning = block.get("reasoning")
            if isinstance(reasoning, str) and reasoning:
                segments.append(StreamSegment("thinking", reasoning))
        elif block_type == "thinking" or "thinking" in block:
            thinking = block.get("thinking")
            if isinstance(thinking, str) and thinking:
                segments.append(StreamSegment("thinking", thinking))
        elif block_type == "text" or block_type is None:
            text = block.get("text")
            if isinstance(text, str) and text:
                segments.append(StreamSegment("text", text))
    return segments


def content_text(content: Any) -> str:
    return "".join(segment.content for segment in content_segments(content) if segment.kind == "text")


async def stream_events(agent: CompiledStateGraph, prompt: str, thread_id: UUID) -> AsyncIterator[StreamSegment]:
    try:
        async for event in agent.astream_events(
            {"messages": [("user", prompt)]},
            config={"recursion_limit": settings.RECURSION_LIMIT, "configurable": {"thread_id": thread_id}},
            version="v2",
        ):
            if not isinstance(event, dict) or event.get("event") != "on_chat_model_stream":
                continue
            data = event.get("data")
            if not isinstance(data, dict):
                continue
            chunk = data.get("chunk")
            content = getattr(chunk, "content", "")
            for segment in content_segments(content):
                yield segment
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
    async for segment in stream_events(agent, prompt, thread_id):
        if segment.kind == "thinking":
            print_thinking(segment.content)
            thinking_contents.append(segment.content)
        else:
            print_stream(segment.content)
            contents.append(segment.content)
    print_stream("\n")
    complete_output = "".join(contents)
    thinking_output = "".join(thinking_contents)
    await SessionOutput.save_output(
        thread_id,
        prompt,
        complete_output,
        complete_output,
        thinking_output=thinking_output or None,
    )
