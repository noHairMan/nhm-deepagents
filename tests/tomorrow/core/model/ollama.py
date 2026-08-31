from types import SimpleNamespace
from unittest.mock import patch

from tomorrow.core.model.callbacks import llm_callback
from tomorrow.core.model.ollama import get_model


class TestOllama:
    def test_get_model(self):
        with patch("tomorrow.core.model.ollama.ChatOllama") as mock_ollama:
            model_config = {"model": "test-model", "base_url": "http://localhost", "temperature": 0.2}
            with (
                patch("tomorrow.core.model.ollama.ModelType", SimpleNamespace(OLLAMA="ollama")),
                patch("tomorrow.conf.settings.MODEL", {"ollama": model_config}),
            ):
                get_model()
                mock_ollama.assert_called_once_with(
                    model=model_config.get("model"),
                    base_url=model_config.get("base_url"),
                    temperature=model_config.get("temperature"),
                    callbacks=[llm_callback],
                )
