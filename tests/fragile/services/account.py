import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from fragile.models.account import InvalidAccountError
from fragile.services.account import AccountService


class MockConfig:
    def __init__(self) -> None:
        self.base_url = ""
        self.api_key = ""
        self.model = ""


class MockModel:
    def __init__(self) -> None:
        self.anthropic = MockConfig()
        self.openai = MockConfig()
        self.type = None


class MockSettings:
    def __init__(self) -> None:
        self.MODEL = MockModel()


class TestAccountService:
    @pytest.mark.asyncio
    async def test_persistence(self, tmp_path, session_factory: async_sessionmaker[AsyncSession]) -> None:
        service = AccountService(session_factory)

        # Save credentials
        await service.save_credentials("openai", "sk-123", "https://api.openai.com")

        # Get credentials
        creds = await service.get_credentials()
        assert creds == ("openai", "sk-123", "https://api.openai.com")

        # Save model
        await service.save_model_selection("openai", "gpt-4")

        # Get model
        model = await service.get_model_selection()
        assert model == ("openai", "gpt-4")

    @pytest.mark.asyncio
    async def test_get_none(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        service = AccountService(session_factory)
        assert await service.get_credentials() is None
        assert await service.get_model_selection() is None

    @pytest.mark.asyncio
    async def test_invalid_model(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        service = AccountService(session_factory)
        await service.save_credentials("openai", "sk-123", "https://api.openai.com")
        with pytest.raises(InvalidAccountError):
            await service.save_model_selection("anthropic", "claude-3")

    @pytest.mark.asyncio
    async def test_restore_configuration(self, session_factory: async_sessionmaker[AsyncSession], monkeypatch) -> None:
        service = AccountService(session_factory)
        await service.save_credentials("openai", "sk-123", "https://api.openai.com")
        await service.save_model_selection("openai", "gpt-4")

        # Mock Tomorrow settings
        mock_settings = MockSettings()
        monkeypatch.setattr("fragile.services.account.tomorrow_settings", mock_settings)

        # Test successful restore
        success = await service.restore_configuration()
        assert success is True
        assert mock_settings.MODEL.openai.api_key == "sk-123"
        assert mock_settings.MODEL.openai.model == "gpt-4"

    @pytest.mark.asyncio
    async def test_restore_configuration_no_account(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        service = AccountService(session_factory)
        assert await service.restore_configuration() is False

    @pytest.mark.asyncio
    async def test_restore_configuration_invalid_provider(
        self, session_factory: async_sessionmaker[AsyncSession], monkeypatch
    ) -> None:
        service = AccountService(session_factory)
        await service.save_credentials("invalid", "key", "https://url.com")

        with pytest.raises(InvalidAccountError):
            await service.restore_configuration()

    @pytest.mark.asyncio
    async def test_restore_configuration_no_model(
        self, session_factory: async_sessionmaker[AsyncSession], monkeypatch
    ) -> None:
        service = AccountService(session_factory)
        await service.save_credentials("openai", "sk-123", "https://api.openai.com")
        # Don't save a model

        mock_settings = MockSettings()
        monkeypatch.setattr("fragile.services.account.tomorrow_settings", mock_settings)

        await service.restore_configuration()
        assert mock_settings.MODEL.openai.model == ""
