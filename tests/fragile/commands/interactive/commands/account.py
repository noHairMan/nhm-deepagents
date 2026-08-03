from uuid import UUID

import pytest

from fragile.commands.interactive.commands.account import AccountCommand
from fragile.models import SessionState
from fragile.models.constants import CommandResult


class TestAccountCommand:
    @pytest.mark.asyncio
    async def test_handle_interactively_saves_selected_provider_credentials(self, monkeypatch, capsys) -> None:
        saved: dict[str, str] = {}

        async def select_provider(self) -> str:
            return "OpenAI"

        class FakePromptSession:
            async def prompt_async(self, message: str, **kwargs: object) -> str:
                return "https://api.example.com" if "base URL" in message else "secret-key"

        async def save_credentials(provider: str, api_key: str, base_url: str) -> None:
            saved.update(provider=provider, api_key=api_key, base_url=base_url)

        monkeypatch.setattr(AccountCommand, "_select_provider", select_provider)
        monkeypatch.setattr("fragile.commands.interactive.commands.account.PromptSession", FakePromptSession)
        monkeypatch.setattr("fragile.commands.interactive.commands.account.Account.save_credentials", save_credentials)
        result = await AccountCommand().handle(None, SessionState(thread_id=UUID(int=1)))
        assert result is CommandResult.CONTINUE
        assert saved == {"provider": "OpenAI", "api_key": "secret-key", "base_url": "https://api.example.com"}
        assert "secret-key" not in capsys.readouterr().out

    @pytest.mark.asyncio
    async def test_handle_does_not_prompt_or_save_when_selection_is_cancelled(self, monkeypatch, capsys) -> None:
        async def select_provider(self) -> None:
            return None

        async def save_credentials(provider: str, api_key: str, base_url: str) -> None:
            raise AssertionError("credentials should not be saved")

        monkeypatch.setattr(AccountCommand, "_select_provider", select_provider)
        monkeypatch.setattr("fragile.commands.interactive.commands.account.Account.save_credentials", save_credentials)
        result = await AccountCommand().handle(None, SessionState(thread_id=UUID(int=1)))
        assert result is CommandResult.CONTINUE
        assert capsys.readouterr().out == ""

    @pytest.mark.asyncio
    async def test_handle_reports_validation_error(self, monkeypatch, capsys) -> None:
        async def select_provider(self) -> str:
            return "Anthropic"

        class FakePromptSession:
            async def prompt_async(self, message: str, **kwargs: object) -> str:
                return "not-a-url" if "base URL" in message else "key"

        monkeypatch.setattr(AccountCommand, "_select_provider", select_provider)
        monkeypatch.setattr("fragile.commands.interactive.commands.account.PromptSession", FakePromptSession)
        await AccountCommand().handle(None, SessionState(thread_id=UUID(int=1)))
        assert "Account not saved" in capsys.readouterr().out
