from uuid import UUID

import pytest

from fragile.commands.interactive.commands import account
from fragile.commands.interactive.commands.account import AccountCommand
from fragile.models import SessionState
from fragile.models.constants import CommandResult
from tomorrow.models.constants import ModelType


class TestAccountCommand:
    @pytest.mark.asyncio
    async def test_select_provider_returns_selected_value(self, monkeypatch) -> None:
        callbacks = {}
        labels: list[str] = []

        class FakeKeyBindings:
            def add(self, key: str, **kwargs: object):
                def decorator(callback):
                    callbacks[key] = callback
                    return callback

                return decorator

        class FakeRadioList:
            current_value = ModelType.OLLAMA

            def __init__(self, **kwargs: object) -> None:
                assert AccountCommand.providers == tuple(ModelType)
                assert kwargs["values"] == [(provider, provider.label) for provider in AccountCommand.providers]

        class FakeApplication:
            def __init__(self, **kwargs: object) -> None:
                self.bindings = kwargs["key_bindings"]

            async def run_async(self) -> ModelType:
                event = type("Event", (), {"app": self})()
                callbacks["enter"](event)
                return ModelType.OLLAMA

            def exit(self, *, result: ModelType) -> None:
                assert result is ModelType.OLLAMA

        monkeypatch.setattr(account, "KeyBindings", FakeKeyBindings)
        monkeypatch.setattr(account, "RadioList", FakeRadioList)
        monkeypatch.setattr(account, "Application", FakeApplication)
        monkeypatch.setattr(account, "HSplit", lambda children, **kwargs: children)
        monkeypatch.setattr(account, "Layout", lambda container, **kwargs: container)
        monkeypatch.setattr(account, "Label", lambda text: labels.append(text) or text)
        monkeypatch.setattr(account.Style, "from_dict", lambda styles: styles)

        async def get_credentials() -> tuple[str, str, str]:
            return "openai", "sk-1234567890-secret", "https://configured.example.com"

        monkeypatch.setattr(account.Account, "get_credentials", get_credentials)

        assert await AccountCommand()._select_provider() is ModelType.OLLAMA
        assert labels[-2] == ""
        assert labels[-1] == (
            "Current account for openai:\nBase URL: https://configured.example.com\nAPI key: sk-1************cret"
        )

    @pytest.mark.asyncio
    async def test_select_provider_returns_none_when_cancelled(self, monkeypatch) -> None:
        callbacks = {}

        class FakeKeyBindings:
            def add(self, key: str, **kwargs: object):
                def decorator(callback):
                    callbacks[key] = callback
                    return callback

                return decorator

        class FakeApplication:
            def __init__(self, **kwargs: object) -> None:
                pass

            async def run_async(self) -> None:
                event = type("Event", (), {"app": self})()
                callbacks["escape"](event)

            def exit(self, *, exception: Exception) -> None:
                raise exception

        monkeypatch.setattr(account, "KeyBindings", FakeKeyBindings)
        monkeypatch.setattr(account, "Application", FakeApplication)
        monkeypatch.setattr(account, "HSplit", lambda children, **kwargs: children)
        monkeypatch.setattr(account, "Layout", lambda container, **kwargs: container)
        monkeypatch.setattr(account, "Label", lambda text: text)
        monkeypatch.setattr(account.Style, "from_dict", lambda styles: styles)

        assert await AccountCommand()._select_provider() is None

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

        async def get_credentials() -> None:
            return None

        monkeypatch.setattr("fragile.commands.interactive.commands.account.Account.get_credentials", get_credentials)
        monkeypatch.setattr("fragile.commands.interactive.commands.account.Account.save_credentials", save_credentials)
        result = await AccountCommand().handle(None, SessionState(thread_id=UUID(int=1)))
        assert result is CommandResult.CONTINUE
        assert saved == {"provider": "OpenAI", "api_key": "secret-key", "base_url": "https://api.example.com"}
        assert "secret-key" not in capsys.readouterr().out

    @pytest.mark.asyncio
    @pytest.mark.parametrize("cancel_at", ["base URL", "API key"])
    async def test_handle_returns_to_chat_when_credential_prompt_is_cancelled(
        self, monkeypatch, cancel_at: str
    ) -> None:
        async def select_provider(self) -> str:
            return "OpenAI"

        class FakePromptSession:
            async def prompt_async(self, message: str, **kwargs: object) -> str:
                if cancel_at in message:
                    raise KeyboardInterrupt
                return "https://api.example.com"

        async def save_credentials(provider: str, api_key: str, base_url: str) -> None:
            raise AssertionError("credentials should not be saved")

        monkeypatch.setattr(AccountCommand, "_select_provider", select_provider)
        monkeypatch.setattr(account, "PromptSession", FakePromptSession)
        monkeypatch.setattr(account.Account, "save_credentials", save_credentials)

        result = await AccountCommand().handle(None, SessionState(thread_id=UUID(int=1)))

        assert result is CommandResult.CONTINUE

    @pytest.mark.asyncio
    async def test_handle_binds_escape_to_cancel_credential_prompt(self, monkeypatch) -> None:
        class FakePromptSession:
            async def prompt_async(self, message: str, **kwargs: object) -> str:
                bindings = kwargs["key_bindings"]
                callback = bindings.get_bindings_for_keys(("escape",))[0].handler

                class FakeApplication:
                    def exit(self, **kwargs: object) -> None:
                        raise kwargs["exception"]

                event = type("Event", (), {"app": FakeApplication()})()
                callback(event)
                return "unreachable"

        async def select_provider(self) -> str:
            return "OpenAI"

        monkeypatch.setattr(AccountCommand, "_select_provider", select_provider)
        monkeypatch.setattr(account, "PromptSession", FakePromptSession)

        result = await AccountCommand().handle(None, SessionState(thread_id=UUID(int=1)))

        assert result is CommandResult.CONTINUE

    @pytest.mark.asyncio
    async def test_handle_displays_matching_current_account_with_masked_key(self, monkeypatch, capsys) -> None:
        async def select_provider(self) -> str:
            return "OpenAI"

        async def get_credentials() -> tuple[str, str, str]:
            return "openai", "sk-1234567890-secret", "https://configured.example.com"

        monkeypatch.setattr(AccountCommand, "_select_provider", select_provider)
        monkeypatch.setattr("fragile.commands.interactive.commands.account.Account.get_credentials", get_credentials)

        class FakePromptSession:
            async def prompt_async(self, message: str, **kwargs: object) -> str:
                return "https://new.example.com" if "base URL" in message else "new-key"

        async def save_credentials(provider: str, api_key: str, base_url: str) -> None:
            return None

        monkeypatch.setattr(account, "PromptSession", FakePromptSession)
        monkeypatch.setattr(account.Account, "save_credentials", save_credentials)
        output = await AccountCommand()._current_account_text()
        assert "https://configured.example.com" in output
        assert "sk-1" in output
        assert "cret" in output
        assert "*" in output
        assert "sk-1234567890-secret" not in output

    @pytest.mark.asyncio
    async def test_handle_does_not_display_nonmatching_current_account(self, monkeypatch, capsys) -> None:
        async def select_provider(self) -> str:
            return "OpenAI"

        async def get_credentials() -> tuple[str, str, str]:
            return "anthropic", "anthropic-secret", "https://anthropic.example.com"

        monkeypatch.setattr(AccountCommand, "_select_provider", select_provider)
        monkeypatch.setattr(account.Account, "get_credentials", get_credentials)

        class FakePromptSession:
            async def prompt_async(self, message: str, **kwargs: object) -> str:
                return "https://new.example.com" if "base URL" in message else "new-key"

        async def save_credentials(provider: str, api_key: str, base_url: str) -> None:
            return None

        monkeypatch.setattr(account, "PromptSession", FakePromptSession)
        monkeypatch.setattr(account.Account, "save_credentials", save_credentials)
        await AccountCommand().handle(None, SessionState(thread_id=UUID(int=1)))
        assert "anthropic.example.com" not in capsys.readouterr().out

    def test_mask_api_key_masks_short_keys(self) -> None:
        assert AccountCommand._mask_api_key("short") == "********"

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
