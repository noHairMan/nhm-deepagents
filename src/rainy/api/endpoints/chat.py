import uuid
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    agent_id: str = "react"
    thread_id: UUID = Field(default_factory=uuid.uuid4)


@router.post("/chat")
async def chat(request: ChatRequest):
    return None
