"""Tomorrow Agent communication handling."""

from collections.abc import AsyncIterator
from importlib import import_module
from typing import Any
from uuid import UUID

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph

from fragile.commands.interactive.display import print_stream
from fragile.conf import settings as fragile_settings
from fragile.exceptions import AgentFactoryImportError, AgentFactoryTypeError, AgentGraphTypeError
from tomorrow.conf import settings
from tomorrow.core.checkpoint import get_checkpointer_context


def content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    return "".join(
        block if isinstance(block, str) else block.get("text", "")
        for block in content
        if isinstance(block, str) or isinstance(block, dict) and isinstance(block.get("text"), str)
    )


async def stream_events(agent: CompiledStateGraph, prompt: str, thread_id: UUID) -> AsyncIterator[str]:
    async for event in agent.astream_events(
        {"messages": [("user", prompt)]},
        config={"recursion_limit": settings.RECURSION_LIMIT, "configurable": {"thread_id": thread_id}},
        version="v2",
    ):
        if not isinstance(event, dict) or event.get("event") != "on_chat_model_stream":
            continue
        chunk = event.get("data", {}).get("chunk")
        content = content_text(getattr(chunk, "content", ""))
        if content:
            yield content


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


async def chat(prompt: str, thread_id: UUID) -> None:
    async with get_checkpointer_context() as checkpointer:
        agent = create_agent(checkpointer)
        async for content in stream_events(agent, prompt, thread_id):
            print_stream(content)
    print_stream("\n")
