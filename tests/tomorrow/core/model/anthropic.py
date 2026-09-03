from unittest.mock import patch

from tomorrow.core.model.anthropic import get_model
from tomorrow.core.model.callbacks import llm_callback
from tomorrow.models.constants import ModelType


class TestAnthropic:
    def test_get_model(self):
        with patch("tomorrow.core.model.anthropic.ChatAnthropic") as mock_anthropic:
            from tomorrow.conf import settings
            from tomorrow.settings import ModelConfig

            new_model_data = settings.MODEL.model_dump()
            new_model_data.pop("type")
            new_model = ModelConfig(type=ModelType.ANTHROPIC, **new_model_data)

            with patch("tomorrow.conf.settings.MODEL", new_model):
                get_model()
                model_config = settings.MODEL.get(ModelType.ANTHROPIC)
                mock_anthropic.assert_called_once_with(
                    model=model_config.get("model"),
                    api_key=model_config.get("api_key"),
                    base_url=model_config.get("base_url"),
                    temperature=model_config.get("temperature"),
                    callbacks=[llm_callback],
                )

    def test_get_model_with_thinking(self):
        with patch("tomorrow.core.model.anthropic.ChatAnthropic") as mock_anthropic:
            from tomorrow.conf import settings
            from tomorrow.settings import AnthropicConfig, ModelConfig

            model_config = ModelConfig(
                type=ModelType.ANTHROPIC,
                anthropic=AnthropicConfig(thinking_enabled=True, thinking_budget_tokens=2048),
            )
            with patch("tomorrow.conf.settings.MODEL", model_config):
                get_model()
                mock_anthropic.assert_called_once_with(
                    model=settings.MODEL.get(ModelType.ANTHROPIC).get("model"),
                    api_key=settings.MODEL.get(ModelType.ANTHROPIC).get("api_key"),
                    base_url=settings.MODEL.get(ModelType.ANTHROPIC).get("base_url"),
                    temperature=settings.MODEL.get(ModelType.ANTHROPIC).get("temperature"),
                    callbacks=[llm_callback],
                    thinking={"type": "enabled", "budget_tokens": 2048},
                )
