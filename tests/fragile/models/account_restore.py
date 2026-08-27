import pytest

from fragile.models import Account, restore_account_configuration
from tomorrow.conf import settings
from tomorrow.models.constants import ModelType


class TestAccountRestore:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("provider", "config_name"),
        [("OLLAMA", "ollama"), (" Anthropic ", "anthropic"), ("openai", "openai")],
    )
    async def test_restore_updates_selected_provider_configuration(
        self, monkeypatch, provider: str, config_name: str
    ) -> None:
        async def get_credentials() -> tuple[str, str, str]:
            return provider, "persisted-key", "https://persisted.example/v1"

        monkeypatch.setattr(Account, "get_credentials", get_credentials)
        assert await restore_account_configuration() is True
        assert settings.MODEL.type is ModelType(provider.strip().lower())
        model_config = getattr(settings.MODEL, config_name)
        assert model_config.base_url == "https://persisted.example/v1"
        if config_name != "ollama":
            assert model_config.api_key == "persisted-key"

    @pytest.mark.asyncio
    async def test_restore_rejects_unsupported_provider(self, monkeypatch) -> None:
        async def get_credentials() -> tuple[str, str, str]:
            return "vertex", "persisted-key", "https://persisted.example/v1"

        monkeypatch.setattr(Account, "get_credentials", get_credentials)
        with pytest.raises(ValueError, match="unsupported model provider"):
            await restore_account_configuration()

    @pytest.mark.asyncio
    async def test_restore_keeps_defaults_without_account(self, monkeypatch) -> None:
        async def get_credentials() -> None:
            return None

        monkeypatch.setattr(Account, "get_credentials", get_credentials)
        assert await restore_account_configuration() is False
