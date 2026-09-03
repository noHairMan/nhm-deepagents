from langchain_anthropic import ChatAnthropic

from tomorrow.conf import settings
from tomorrow.core.model.callbacks import llm_callback
from tomorrow.models.constants import ModelType


def get_model() -> ChatAnthropic:
    model_config = settings.MODEL.get(ModelType.ANTHROPIC, {})
    model_kwargs = {
        "model": model_config.get("model"),
        "api_key": model_config.get("api_key"),
        "base_url": model_config.get("base_url"),
        "temperature": model_config.get("temperature", 0),
        "callbacks": [llm_callback],
    }
    if model_config.get("thinking_enabled"):
        model_kwargs["thinking"] = {
            "type": "enabled",
            "budget_tokens": model_config.get("thinking_budget_tokens"),
        }
    return ChatAnthropic(
        **model_kwargs,
    )
