import os
from unittest.mock import patch

from tomorrow.conf import settings as tomorrow_settings
from tomorrow.settings import TomorrowSettings
from tomorrow.utils.functional import SimpleLazyObject


class TestConfig:
    def test_settings_loading(self):
        # 验证 settings 是 SimpleLazyObject
        assert isinstance(tomorrow_settings, SimpleLazyObject)

        # 验证默认配置
        settings = TomorrowSettings(_env_file=None)
        assert settings.MODEL["type"] == "ollama"
        assert settings.MODEL["ollama"]["model"] == "qwen3.5:9b"
        assert settings.MODEL["ollama"]["base_url"].startswith("http")
        assert settings.RECURSION_LIMIT == 100

    def test_settings_override_with_env(self):
        # 模拟环境变量覆盖
        with patch.dict(os.environ, {"TOMORROW_MODEL__OLLAMA__MODEL": "gpt-4"}):
            new_settings = TomorrowSettings(_env_file=None)
            assert new_settings.MODEL["ollama"]["model"] == "gpt-4"

        with patch.dict(os.environ, {"TOMORROW_RECURSION_LIMIT": "100"}):
            new_settings = TomorrowSettings(_env_file=None)
            assert new_settings.RECURSION_LIMIT == 100

    def test_custom_settings_module(self):
        # 测试自定义设置模块
        with patch.dict(os.environ, {"TOMORROW_SETTINGS_MODULE": "tomorrow.settings"}):
            new_settings = TomorrowSettings(_env_file=None)
            assert new_settings.APP.upper() == "TOMORROW"
