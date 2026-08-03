import pytest

from fragile.models import Account, restore_account_configuration
from tomorrow.conf import settings


class TestAccountRestore:
    @pytest.mark.asyncio
    async def test_restore_updates_anthropic_configuration(self, monkeypatch) -> None:
        async def get_credentials() -> tuple[str, str, str]:
            return "anthropic", "persisted-key", "https://persisted.example/v1"

        monkeypatch.setattr(Account, "get_credentials", get_credentials)
        settings.MODEL.type = "ollama"
        assert await restore_account_configuration() is True
        assert settings.MODEL.type == "anthropic"
        assert settings.MODEL.anthropic.api_key == "persisted-key"
        assert settings.MODEL.anthropic.base_url == "https://persisted.example/v1"

    @pytest.mark.asyncio
    async def test_restore_keeps_defaults_without_account(self, monkeypatch) -> None:
        async def get_credentials() -> None:
            return None

        monkeypatch.setattr(Account, "get_credentials", get_credentials)
        assert await restore_account_configuration() is False
