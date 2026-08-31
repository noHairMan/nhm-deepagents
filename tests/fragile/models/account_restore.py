import pytest

from fragile.models import Account, restore_account_configuration
from tomorrow.conf import settings
from tomorrow.models.constants import ModelType


class TestAccountRestore:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("provider", "config_name"),
        [(" Anthropic ", "anthropic"), ("openai", "openai")],
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

    @pytest.mark.asyncio
    async def test_restore_applies_persisted_model_for_account_provider(self, monkeypatch) -> None:
        async def get_credentials() -> tuple[str, str, str]:
            return "openai", "persisted-key", "https://persisted.example/v1"

        async def get_model_selection() -> tuple[str, str]:
            return "openai", "gpt-5"

        monkeypatch.setattr(Account, "get_credentials", get_credentials)
        monkeypatch.setattr(Account, "get_model_selection", get_model_selection)
        assert await restore_account_configuration() is True
        assert settings.MODEL.openai.model == "gpt-5"

    @pytest.mark.asyncio
    async def test_restore_keeps_model_default_without_persisted_selection(self, monkeypatch) -> None:
        async def get_credentials() -> tuple[str, str, str]:
            return "openai", "persisted-key", "https://persisted.example/v1"

        async def get_model_selection() -> None:
            return None

        monkeypatch.setattr(Account, "get_credentials", get_credentials)
        monkeypatch.setattr(Account, "get_model_selection", get_model_selection)
        assert await restore_account_configuration() is True

    @pytest.mark.asyncio
    async def test_restore_ignores_model_for_different_provider(self, monkeypatch) -> None:
        async def get_credentials() -> tuple[str, str, str]:
            return "openai", "persisted-key", "https://persisted.example/v1"

        async def get_model_selection() -> tuple[str, str]:
            return "anthropic", "claude-sonnet-5"

        monkeypatch.setattr(Account, "get_credentials", get_credentials)
        monkeypatch.setattr(Account, "get_model_selection", get_model_selection)
        previous_model = settings.MODEL.openai.model
        assert await restore_account_configuration() is True
        assert settings.MODEL.openai.model == previous_model
