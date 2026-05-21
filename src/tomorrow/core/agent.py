from typing import Optional

from deepagents import create_deep_agent
from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama

from tomorrow.utils.conf import settings


def get_model(model: Optional[str] = None) -> BaseChatModel:
    model = model or settings.DEFAULT_MODEL
    return ChatOllama(
        model=model,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0,
    )


assistant_instructions = """你是一名编码助理，主要语言是使用python。 """

agent = create_deep_agent(
    model=get_model(),
    memory=[],
    tools=[],
    skills=[],
    system_prompt=assistant_instructions,
)
