import time
from collections.abc import AsyncIterable
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from rainy.dependencies import get_agent

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    thread_id: UUID = Field(default_factory=uuid4)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str | None = None


class ChatUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str = "deepagent"
    choices: list[ChatChoice]
    usage: ChatUsage = Field(default_factory=ChatUsage)


class ChatStreamDelta(BaseModel):
    role: str | None = None
    content: str | None = None


class ChatStreamChoice(BaseModel):
    index: int
    delta: ChatStreamDelta
    finish_reason: str | None = None


class ChatStreamResponse(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str = "deepagent"
    choices: list[ChatStreamChoice]


@router.post("/chat", response_class=JSONResponse)
async def chat(
    request: ChatRequest,
    agent: Any = Depends(get_agent),
) -> ChatResponse:
    """同步接口：一次性返回智能体生成的完整回答。"""
    result = await agent.ainvoke(
        {"messages": [("user", request.message)]},
        config={"configurable": {"thread_id": request.thread_id}},
    )
    answer = result["messages"][-1].content

    return ChatResponse(
        id=f"chatcmpl-{request.thread_id}",
        choices=[
            ChatChoice(
                index=0,
                message=ChatMessage(role="assistant", content=answer),
                finish_reason="stop",
            )
        ],
        usage=ChatUsage(),  # 暂不计算具体 token
    )


@router.post("/chat/stream", response_class=EventSourceResponse)
async def chat_stream(
    request: ChatRequest,
    agent: Any = Depends(get_agent),
) -> AsyncIterable[ServerSentEvent]:
    """流式接口：以 SSE 形式逐 token 输出智能体生成的内容。"""
    chat_id = f"chatcmpl-{request.thread_id}"
    created_time = int(time.time())

    async for event in agent.astream_events(
        {"messages": [("user", request.message)]},
        config={"configurable": {"thread_id": request.thread_id}},
        version="v2",
    ):
        if event["event"] == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            content = getattr(chunk, "content", "")
            if content:
                response = ChatStreamResponse(
                    id=chat_id,
                    created=created_time,
                    choices=[
                        ChatStreamChoice(
                            index=0,
                            delta=ChatStreamDelta(content=content),
                        )
                    ],
                )
                yield ServerSentEvent(raw_data=response.model_dump_json())
        elif event["event"] == "on_chat_model_end":
            response = ChatStreamResponse(
                id=chat_id,
                created=created_time,
                choices=[
                    ChatStreamChoice(
                        index=0,
                        delta=ChatStreamDelta(),
                        finish_reason="stop",
                    )
                ],
            )
            yield ServerSentEvent(raw_data=response.model_dump_json())
