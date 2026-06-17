from unittest.mock import patch

import pytest

from tomorrow.core.model import get_model
from tomorrow.models.constants import ModelType


class TestModels:
    def test_get_model_ollama(self):
        with patch("tomorrow.core.model.ollama.get_model") as mock_get_model:
            from tomorrow.conf import settings

            with patch.dict(settings.MODEL, {"type": ModelType.OLLAMA}):
                get_model()
                mock_get_model.assert_called_once()

    def test_get_model_huggingface(self):
        with patch("tomorrow.core.model.huggingface.get_model") as mock_get_model:
            from tomorrow.conf import settings

            with patch.dict(settings.MODEL, {"type": ModelType.HUGGINGFACE}):
                get_model()
                mock_get_model.assert_called_once()

    def test_get_model_unsupported_type(self):
        from tomorrow.conf import settings

        with patch.dict(settings.MODEL, {"type": "unsupported"}):
            with pytest.raises(ValueError, match="Unsupported model type: unsupported"):
                get_model()
