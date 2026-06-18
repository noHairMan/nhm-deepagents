from unittest.mock import patch

from tomorrow.core.model.ollama import get_model
from tomorrow.models.constants import ModelType


class TestOllama:
    def test_get_model(self):
        with patch("tomorrow.core.model.ollama.ChatOllama") as mock_ollama:
            from tomorrow.conf import settings
            from tomorrow.settings import ModelConfig

            new_model_data = settings.MODEL.model_dump()
            new_model_data.pop("type")
            new_model = ModelConfig(type=ModelType.OLLAMA, **new_model_data)

            with patch("tomorrow.conf.settings.MODEL", new_model):
                get_model()
                model_config = settings.MODEL.get(ModelType.OLLAMA)
                mock_ollama.assert_called_once_with(
                    model=model_config.get("model"),
                    base_url=model_config.get("base_url"),
                    temperature=model_config.get("temperature"),
                )
