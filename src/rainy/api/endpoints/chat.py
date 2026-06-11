from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from fastapi.sse import EventSourceResponse
from pydantic import BaseModel, Field

from rainy.dependencies import get_agent

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    thread_id: UUID = Field(default_factory=uuid4)


@router.post("/chat")
async def chat(request: ChatRequest, agent: Any = Depends(get_agent)) -> str:
    response = await agent.ainvoke(
        {"messages": [("user", request.message)]},
        config={"configurable": {"thread_id": request.thread_id}},
        version="v2",
    )
    return response.value["messages"][-1].content


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    agent: Any = Depends(get_agent),
) -> EventSourceResponse:

    async def event_generator():
        async for event in agent.astream(
            {"messages": [("user", request.message)]},
            config={"configurable": {"thread_id": request.thread_id}},
            version="v2",
        ):
            yield f"data: {event}\n\n"

    return EventSourceResponse(event_generator())


@router.post("/chat/stream/event")
async def chat_stream_event(
    request: ChatRequest,
    agent: Any = Depends(get_agent),
) -> EventSourceResponse:

    async def event_generator():
        async for event in agent.astream_events(
            {"messages": [("user", request.message)]},
            config={"configurable": {"thread_id": request.thread_id}},
            version="v2",
        ):
            yield f"data: {event}\n\n"

    return EventSourceResponse(event_generator())
