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


research_instructions = """你是一名心理专家，使用心理学知识分析用户心理，并给予用户建议。 """

agent = create_deep_agent(
    model=get_model(),
    tools=[],
    system_prompt=research_instructions,
)
