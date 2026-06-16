from unittest.mock import patch

import pytest

from tomorrow.core.model import get_model
from tomorrow.models.constants import ModelType


class TestModels:
    def test_get_model(self):
        with patch("tomorrow.core.model.ChatOllama") as mock_ollama:
            from tomorrow.conf import settings

            get_model()
            model_config = settings.MODEL.get(ModelType.OLLAMA)
            mock_ollama.assert_called_once_with(
                model=model_config.get("model"),
                base_url=model_config.get("base_url"),
                temperature=model_config.get("temperature"),
            )

    def test_get_model_unsupported_type(self):
        from tomorrow.conf import settings

        with patch.dict(settings.MODEL, {"type": "unsupported"}):
            with pytest.raises(ValueError, match="Unsupported model type: unsupported"):
                get_model()
