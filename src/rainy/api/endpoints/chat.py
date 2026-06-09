import json
import uuid
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from tomorrow.core.agent import create_agent

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


async def stream_chat(message: str) -> AsyncGenerator[str]:
    """以 SSE 形式流式输出智能体生成的内容。"""
    async with create_agent() as agent:
        async for event in agent.astream_events(
            {"messages": [("user", message)]},
            config={"configurable": {"thread_id": str(uuid.uuid4())}},
            version="v2",
        ):
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                content = getattr(chunk, "content", "")
                if content:
                    yield f"data: {json.dumps({'answer': content}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"


@router.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """同步接口：一次性返回智能体生成的完整回答。"""
    async with create_agent() as agent:
        result = await agent.ainvoke(
            {"messages": [("user", request.message)]},
            config={"configurable": {"thread_id": str(uuid.uuid4())}},
        )
    answer = result["messages"][-1].content
    return ChatResponse(answer=answer)


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """流式接口：以 SSE 形式逐 token 输出智能体生成的内容。"""
    return StreamingResponse(stream_chat(request.message), media_type="text/event-stream")
