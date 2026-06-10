from collections.abc import AsyncIterable
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from fastapi.sse import EventSourceResponse
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from rainy.dependencies import get_agent

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    thread_id: UUID = Field(default=uuid4)


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_class=JSONResponse)
async def chat(
    chat_request: ChatRequest,
    agent: Any = Depends(get_agent),
) -> ChatResponse:
    """同步接口：一次性返回智能体生成的完整回答。"""
    result = await agent.ainvoke(
        {"messages": [("user", chat_request.message)]},
        config={"configurable": {"thread_id": chat_request.thread_id}},
    )
    answer = result["messages"][-1].content
    return ChatResponse(answer=answer)


@router.post("/chat/stream", response_class=EventSourceResponse)
async def chat_stream(
    chat_request: ChatRequest,
    agent: Any = Depends(get_agent),
) -> AsyncIterable[ChatResponse]:
    """流式接口：以 SSE 形式逐 token 输出智能体生成的内容。"""
    async for event in agent.astream_events(
        {"messages": [("user", chat_request.message)]},
        config={"configurable": {"thread_id": chat_request.thread_id}},
        version="v2",
    ):
        if event["event"] == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            content = getattr(chunk, "content", "")
            yield ChatResponse(answer=content)
