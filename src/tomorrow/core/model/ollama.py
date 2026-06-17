from langchain_ollama import ChatOllama

from tomorrow.conf import settings
from tomorrow.models.constants import ModelType


def get_model() -> ChatOllama:
    model_config = settings.MODEL.get(ModelType.OLLAMA, {})
    return ChatOllama(
        model=model_config.get("model"),
        base_url=model_config.get("base_url"),
        temperature=model_config.get("temperature", 0),
    )
