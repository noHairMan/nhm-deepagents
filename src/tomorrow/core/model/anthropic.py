from langchain_anthropic import ChatAnthropic

from tomorrow.conf import settings
from tomorrow.models.constants import ModelType


def get_model() -> ChatAnthropic:
    model_config = settings.MODEL.get(ModelType.ANTHROPIC, {})
    return ChatAnthropic(
        model=model_config.get("model"),
        api_key=model_config.get("api_key"),
        base_url=model_config.get("base_url"),
        temperature=model_config.get("temperature", 0),
    )
