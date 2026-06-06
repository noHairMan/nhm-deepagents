import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from tomorrow.core.agent import create_agent

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    async with create_agent() as agent:
        result = await agent.ainvoke(
            {"messages": [("user", request.message)]},
            config={"configurable": {"thread_id": str(uuid.uuid4())}},
        )
        answer = result["messages"][-1].content
        return ChatResponse(answer=answer)
