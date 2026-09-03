import os
from unittest.mock import patch

import pytest

from tomorrow.conf import settings as tomorrow_settings
from tomorrow.settings import TomorrowSettings
from tomorrow.utils.functional import SimpleLazyObject


class TestConfig:
    def test_settings_loading(self):
        # 验证 settings 是 SimpleLazyObject
        assert isinstance(tomorrow_settings, SimpleLazyObject)

        # 验证默认配置
        settings = TomorrowSettings(_env_file=None)
        assert settings.MODEL["type"] == "anthropic"
        assert settings.MODEL["anthropic"]["model"] == "claude-sonnet-5"
        assert settings.MODEL["anthropic"]["base_url"] is None
        assert settings.MODEL["anthropic"]["thinking_enabled"] is False
        assert settings.MODEL["anthropic"]["thinking_budget_tokens"] is None
        assert settings.MODEL["openai"]["reasoning_effort"] is None
        assert settings.MODEL["openai"]["reasoning_summary"] is None
        assert settings.SKILLS == []
        assert settings.RECURSION_LIMIT == 100

    def test_settings_override_with_env(self):
        # 模拟环境变量覆盖
        with patch.dict(os.environ, {"TOMORROW_MODEL__ANTHROPIC__MODEL": "claude-test"}):
            new_settings = TomorrowSettings(_env_file=None)
            assert new_settings.MODEL["anthropic"]["model"] == "claude-test"

        with patch.dict(
            os.environ,
            {
                "TOMORROW_MODEL__ANTHROPIC__THINKING_ENABLED": "true",
                "TOMORROW_MODEL__ANTHROPIC__THINKING_BUDGET_TOKENS": "2048",
                "TOMORROW_MODEL__OPENAI__REASONING_EFFORT": "high",
                "TOMORROW_MODEL__OPENAI__REASONING_SUMMARY": "detailed",
            },
        ):
            new_settings = TomorrowSettings(_env_file=None)
            assert new_settings.MODEL["anthropic"]["thinking_enabled"] is True
            assert new_settings.MODEL["anthropic"]["thinking_budget_tokens"] == 2048
            assert new_settings.MODEL["openai"]["reasoning_effort"] == "high"
            assert new_settings.MODEL["openai"]["reasoning_summary"] == "detailed"

        with pytest.raises(ValueError, match="thinking_budget_tokens"):
            TomorrowSettings(
                _env_file=None,
                MODEL={"anthropic": {"thinking_enabled": True}},
            )

        with pytest.raises(ValueError):
            TomorrowSettings(
                _env_file=None,
                MODEL={"openai": {"reasoning_effort": "invalid"}},
            )

        with patch.dict(os.environ, {"TOMORROW_RECURSION_LIMIT": "100"}):
            new_settings = TomorrowSettings(_env_file=None)
            assert new_settings.RECURSION_LIMIT == 100

        with patch.dict(os.environ, {"TOMORROW_SKILLS": '["custom-skills/"]'}):
            new_settings = TomorrowSettings(_env_file=None)
            assert new_settings.SKILLS == ["custom-skills/"]

    def test_custom_settings_module(self):
        # 测试自定义设置模块
        with patch.dict(os.environ, {"TOMORROW_SETTINGS_MODULE": "tomorrow.settings"}):
            new_settings = TomorrowSettings(_env_file=None)
            assert new_settings.APP.upper() == "TOMORROW"
