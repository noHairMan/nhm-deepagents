from langchain_core.language_models import BaseChatModel

from tomorrow.conf import settings
from tomorrow.exceptions import TomorrowModelError
from tomorrow.models.constants import ModelType


def get_model() -> BaseChatModel:
    model_type = settings.MODEL.get("type")
    match model_type:
        case ModelType.OLLAMA:
            from .ollama import get_model as get_ollama_model

            return get_ollama_model()
        case ModelType.HUGGINGFACE:
            from .huggingface import get_model as get_huggingface_model

            return get_huggingface_model()
        case ModelType.ANTHROPIC:
            from .anthropic import get_model as get_anthropic_model

            return get_anthropic_model()
        case _:
            raise TomorrowModelError(f"Unsupported model type: {model_type}")
