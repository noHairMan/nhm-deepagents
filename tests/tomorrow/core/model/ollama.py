from unittest.mock import patch

from tomorrow.core.model.ollama import get_model
from tomorrow.models.constants import ModelType


class TestOllama:
    def test_get_model(self):
        with patch("tomorrow.core.model.ollama.ChatOllama") as mock_ollama:
            from tomorrow.conf import settings

            with patch.dict(settings.MODEL, {"type": ModelType.OLLAMA}):
                get_model()
                model_config = settings.MODEL.get(ModelType.OLLAMA)
                mock_ollama.assert_called_once_with(
                    model=model_config.get("model"),
                    base_url=model_config.get("base_url"),
                    temperature=model_config.get("temperature"),
                )
