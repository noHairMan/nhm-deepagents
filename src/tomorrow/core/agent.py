import contextlib
from typing import Optional

from deepagents import create_deep_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama

from tomorrow.conf import settings
from tomorrow.core.checkpoints import get_checkpointer_context


def get_model(model: Optional[str] = None) -> BaseChatModel:
    model = model or settings.DEFAULT_MODEL
    return ChatOllama(
        model=model,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0,
    )


@contextlib.asynccontextmanager
async def create_agent():
    async with get_checkpointer_context() as checkpointer:
        yield create_deep_agent(
            model=get_model(),
            memory=[],
            tools=[],
            skills=[],
            system_prompt=SystemMessage(content="""你是一名智能助理，运用你的知识尽可能的回答用户问题。"""),
            checkpointer=checkpointer,
        )
