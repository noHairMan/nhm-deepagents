import json
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from fastapi.sse import EventSourceResponse
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field

from tomorrow.conf import settings
from tomorrow.core.agent import AgentManager

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    thread_id: UUID = Field(default_factory=uuid4)


@router.post("/chat")
async def chat(request: ChatRequest, agent: CompiledStateGraph = Depends(AgentManager.get_agent)) -> str:
    response = await agent.ainvoke(
        {"messages": [("user", request.message)]},
        config={
            "recursion_limit": settings.RECURSION_LIMIT,
            "configurable": {"thread_id": request.thread_id},
        },
        stream_mode="values",
        version="v2",
    )
    return response.value["messages"][-1].content


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    agent: CompiledStateGraph = Depends(AgentManager.get_agent),
) -> EventSourceResponse:

    async def event_generator():
        async for event in agent.astream_events(
            {"messages": [("user", request.message)]},
            config={
                "recursion_limit": settings.RECURSION_LIMIT,
                "configurable": {"thread_id": request.thread_id},
            },
            version="v2",
        ):
            if not isinstance(event, dict):
                continue
            if event.get("event") == "on_chat_model_stream":
                content = event.get("data", {}).get("chunk", {}).content
                if content:
                    payload = json.dumps({"content": content}, ensure_ascii=False)
                    yield f"data: {payload}\n\n"

    return EventSourceResponse(event_generator())


@router.post("/chat/stream/event")
async def chat_stream_event(
    request: ChatRequest,
    agent: CompiledStateGraph = Depends(AgentManager.get_agent),
) -> EventSourceResponse:

    async def event_generator():
        async for event in agent.astream_events(
            {"messages": [("user", request.message)]},
            config={
                "recursion_limit": settings.RECURSION_LIMIT,
                "configurable": {"thread_id": request.thread_id},
            },
            version="v2",
        ):
            try:
                payload = json.dumps(event, ensure_ascii=False)
            except TypeError, ValueError:
                # 如果 event 中包含不可序列化的对象（如 AIMessageChunk），则转换为字符串
                payload = json.dumps(str(event), ensure_ascii=False)
            yield f"data: {payload}\n\n"

    return EventSourceResponse(event_generator())
