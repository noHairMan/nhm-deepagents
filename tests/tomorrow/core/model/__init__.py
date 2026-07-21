from unittest.mock import patch

import pytest

from tomorrow.core.model import get_model
from tomorrow.exceptions import TomorrowModelError
from tomorrow.models.constants import ModelType


class TestModels:
    def test_get_model_ollama(self):
        with patch("tomorrow.core.model.ollama.get_model") as mock_get_model:
            from tomorrow.conf import settings
            from tomorrow.settings import ModelConfig

            new_model_data = settings.MODEL.model_dump()
            new_model_data.pop("type")
            new_model = ModelConfig(type=ModelType.OLLAMA, **new_model_data)

            with patch("tomorrow.conf.settings.MODEL", new_model):
                get_model()
                mock_get_model.assert_called_once()

    def test_get_model_huggingface(self):
        with patch("tomorrow.core.model.huggingface.get_model") as mock_get_model:
            from tomorrow.conf import settings
            from tomorrow.settings import ModelConfig

            new_model_data = settings.MODEL.model_dump()
            new_model_data.pop("type")
            new_model = ModelConfig(type=ModelType.HUGGINGFACE, **new_model_data)

            with patch("tomorrow.conf.settings.MODEL", new_model):
                get_model()
                mock_get_model.assert_called_once()

    def test_get_model_anthropic(self):
        with patch("tomorrow.core.model.anthropic.get_model") as mock_get_model:
            from tomorrow.conf import settings
            from tomorrow.settings import ModelConfig

            new_model_data = settings.MODEL.model_dump()
            new_model_data.pop("type")
            new_model = ModelConfig(type=ModelType.ANTHROPIC, **new_model_data)

            with patch("tomorrow.conf.settings.MODEL", new_model):
                get_model()
                mock_get_model.assert_called_once()

    def test_get_model_unsupported_type(self):
        from unittest.mock import MagicMock

        mock_model = MagicMock()
        mock_model.get.return_value = "unsupported"

        with patch("tomorrow.conf.settings.MODEL", mock_model):
            with pytest.raises(TomorrowModelError, match="Unsupported model type: unsupported"):
                get_model()
