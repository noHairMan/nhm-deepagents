from unittest.mock import patch

from tomorrow.core.models import get_model


class TestModels:
    def test_get_model(self):
        with patch("tomorrow.core.models.ChatOllama") as mock_ollama:
            from tomorrow.conf import settings

            get_model("test-model")
            mock_ollama.assert_called_once_with(
                model="test-model",
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0,
            )

    def test_get_model_default(self):
        with patch("tomorrow.core.models.ChatOllama") as mock_ollama:
            from tomorrow.conf import settings

            get_model()
            mock_ollama.assert_called_once_with(
                model="qwen3.5:9b",
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0,
            )
