from unittest.mock import patch

from tomorrow.core.model.huggingface import get_model
from tomorrow.models.constants import ModelType


class TestHuggingface:
    def test_get_model(self):
        with (
            patch("tomorrow.core.model.huggingface.HuggingFaceEndpoint") as mock_endpoint,
            patch("tomorrow.core.model.huggingface.ChatHuggingFace") as mock_chat,
        ):
            from tomorrow.conf import settings
            from tomorrow.settings import ModelConfig

            new_model_data = settings.MODEL.model_dump()
            new_model_data.pop("type")
            new_model = ModelConfig(type=ModelType.HUGGINGFACE, **new_model_data)

            with patch("tomorrow.conf.settings.MODEL", new_model):
                get_model()
                model_config = settings.MODEL.get(ModelType.HUGGINGFACE)
                mock_endpoint.assert_called_once_with(
                    endpoint_url=model_config.get("url"),
                    repo_id=model_config.get("model"),
                    task="text-generation",
                    huggingfacehub_api_token=model_config.get("api_key"),
                    temperature=model_config.get("temperature"),
                )
                mock_chat.assert_called_once_with(llm=mock_endpoint.return_value)
