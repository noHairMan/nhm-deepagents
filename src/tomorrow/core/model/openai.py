from langchain_openai import ChatOpenAI

from tomorrow.conf import settings
from tomorrow.core.model.callbacks import llm_callback
from tomorrow.models.constants import ModelType


def get_model() -> ChatOpenAI:
    model_config = settings.MODEL.get(ModelType.OPENAI, {})
    return ChatOpenAI(
        model=model_config.get("model"),
        api_key=model_config.get("api_key"),
        base_url=model_config.get("base_url"),
        temperature=model_config.get("temperature", 0),
        callbacks=[llm_callback],
    )
