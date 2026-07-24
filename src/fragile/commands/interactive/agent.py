"""Tomorrow Agent communication handling."""

from collections.abc import AsyncIterator
from typing import Any
from uuid import UUID

from langgraph.graph.state import CompiledStateGraph

from tomorrow.conf import settings
from tomorrow.core.agent import AgentManager
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


async def chat(prompt: str, thread_id: UUID, output: Any) -> None:
    async with get_checkpointer_context() as checkpointer:
        agent = AgentManager.create_agent(checkpointer)
        async for content in stream_events(agent, prompt, thread_id):
            output(content)
    output("\n")
