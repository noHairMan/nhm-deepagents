from unittest.mock import patch

from tomorrow.core.model.callbacks import llm_callback
from tomorrow.core.model.openai import get_model
from tomorrow.models.constants import ModelType


class TestOpenAI:
    def test_get_model(self):
        with patch("tomorrow.core.model.openai.ChatOpenAI") as mock_openai:
            from tomorrow.conf import settings
            from tomorrow.settings import ModelConfig

            new_model_data = settings.MODEL.model_dump()
            new_model_data.pop("type")
            new_model = ModelConfig(type=ModelType.OPENAI, **new_model_data)

            with patch("tomorrow.conf.settings.MODEL", new_model):
                get_model()
                model_config = settings.MODEL.get(ModelType.OPENAI)
                mock_openai.assert_called_once_with(
                    model=model_config.get("model"),
                    api_key=model_config.get("api_key"),
                    base_url=model_config.get("base_url"),
                    temperature=model_config.get("temperature"),
                    callbacks=[llm_callback],
                )

    def test_get_model_with_reasoning(self):
        with patch("tomorrow.core.model.openai.ChatOpenAI") as mock_openai:
            from tomorrow.conf import settings
            from tomorrow.settings import ModelConfig, OpenAIConfig

            model_config = ModelConfig(
                type=ModelType.OPENAI,
                openai=OpenAIConfig(reasoning_effort="high", reasoning_summary="detailed"),
            )
            with patch("tomorrow.conf.settings.MODEL", model_config):
                get_model()
                mock_openai.assert_called_once_with(
                    model=settings.MODEL.get(ModelType.OPENAI).get("model"),
                    api_key=settings.MODEL.get(ModelType.OPENAI).get("api_key"),
                    base_url=settings.MODEL.get(ModelType.OPENAI).get("base_url"),
                    temperature=settings.MODEL.get(ModelType.OPENAI).get("temperature"),
                    callbacks=[llm_callback],
                    reasoning_effort="high",
                    reasoning={"summary": "detailed"},
                )
