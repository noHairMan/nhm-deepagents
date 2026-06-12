from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama

from tomorrow.conf import settings


def get_model(model: Optional[str] = None) -> BaseChatModel:
    model = model or settings.DEFAULT_MODEL
    return ChatOllama(
        model=model,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0,
    )
