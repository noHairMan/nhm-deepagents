import os
from unittest.mock import patch

from tomorrow.conf import settings as tomorrow_settings
from tomorrow.utils.functional import SimpleLazyObject


class TestConfig:
    def test_settings_loading(self):
        # 验证 settings 是 SimpleLazyObject
        assert isinstance(tomorrow_settings, SimpleLazyObject)

        # 验证默认配置
        assert tomorrow_settings.MODEL["type"] == "ollama"
        assert tomorrow_settings.MODEL["ollama"]["model"] == "qwen3.5:9b"
        # 允许从环境变量加载的不同 base_url
        assert tomorrow_settings.MODEL["ollama"]["base_url"].startswith("http")

    def test_settings_override_with_env(self):
        # 模拟环境变量覆盖
        with patch.dict(os.environ, {"TOMORROW_MODEL__OLLAMA__MODEL": "gpt-4"}):
            # 由于 settings 是 LazyObject 且可能已经被初始化，我们需要重新获取或清理
            # 但在 dynaconf 中，环境变量通常会自动生效，如果还没加载的话。
            # 这里我们测试重新加载逻辑或直接验证环境变量优先级
            from tomorrow.conf.config import _get_settings

            new_settings = _get_settings()
            assert new_settings.MODEL["ollama"]["model"] == "gpt-4"

    def test_custom_settings_module(self):
        # 测试自定义设置模块
        with patch.dict(os.environ, {"TOMORROW_SETTINGS_MODULE": "tomorrow.settings"}):
            from tomorrow.conf.config import _get_settings

            new_settings = _get_settings()
            assert new_settings.APP.upper() == "TOMORROW"
