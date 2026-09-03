from langchain_openai import ChatOpenAI

from tomorrow.conf import settings
from tomorrow.core.model.callbacks import llm_callback
from tomorrow.models.constants import ModelType


def get_model() -> ChatOpenAI:
    model_config = settings.MODEL.get(ModelType.OPENAI, {})
    model_kwargs = {
        "model": model_config.get("model"),
        "api_key": model_config.get("api_key"),
        "base_url": model_config.get("base_url"),
        "temperature": model_config.get("temperature", 0),
        "callbacks": [llm_callback],
    }
    if model_config.get("reasoning_effort"):
        model_kwargs["reasoning_effort"] = model_config.get("reasoning_effort")
    if model_config.get("reasoning_summary"):
        model_kwargs["reasoning"] = {"summary": model_config.get("reasoning_summary")}
    return ChatOpenAI(**model_kwargs)
