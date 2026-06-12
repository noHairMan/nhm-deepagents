from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama

from tomorrow.conf import settings
from tomorrow.models.constants import ModelType


def get_model() -> BaseChatModel:
    model_type = settings.MODEL.get("type")
    model_config = settings.MODEL.get(model_type, {})
    match model_type:
        case ModelType.OLLAMA:
            return ChatOllama(
                model=model_config.get("model"),
                base_url=model_config.get("base_url"),
                temperature=model_config.get("temperature", 0),
            )
        case _:
            raise ValueError(f"Unsupported model type: {model_type}")
