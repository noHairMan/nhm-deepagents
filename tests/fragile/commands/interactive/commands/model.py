from unittest.mock import AsyncMock, MagicMock, Mock, call, patch
from uuid import UUID

import asyncclick as click
import httpx
import pytest

from fragile.commands.interactive.commands.model import (
    ANTHROPIC_VERSION,
    ModelCommand,
    _response_model_names,
    build_model_options,
    choose_model,
    discover_models,
)
from fragile.models import InvalidAccountError, SessionState
from fragile.models.constants import CommandResult
from tomorrow.models.constants import ModelType


class TestModelCommand:
    @pytest.mark.parametrize(
        ("response", "key"),
        [
            ([], "models"),
            ({}, "models"),
            ({"models": ["qwen"]}, "models"),
            ({"models": [{}]}, "models"),
            ({"data": [{"id": " "}]}, "data"),
        ],
    )
    def test_response_model_names_rejects_invalid_collections(self, response: object, key: str) -> None:
        assert _response_model_names(response, key) is None

    def test_build_model_options_groups_providers_and_marks_current_model(self) -> None:
        options = build_model_options(
            {
                ModelType.ANTHROPIC: ("claude",),
                ModelType.OPENAI: ("gpt",),
            },
            (ModelType.OPENAI, "gpt"),
        )

        assert options == [
            ((ModelType.ANTHROPIC, "claude"), "Anthropic  claude"),
            ((ModelType.OPENAI, "gpt"), "OpenAI     gpt  Current model"),
        ]

    @pytest.mark.asyncio
    async def test_choose_model_returns_none_for_empty_options(self, capsys) -> None:
        assert await choose_model([]) is None
        assert "No models are available" in capsys.readouterr().out

    @pytest.mark.asyncio
    async def test_choose_model_returns_none_when_cancelled(self) -> None:
        with patch(
            "fragile.commands.interactive.commands.model.select_history",
            new_callable=AsyncMock,
            side_effect=click.Abort(),
        ):
            assert await choose_model([((ModelType.OPENAI, "gpt"), "OpenAI gpt")]) is None

    @pytest.mark.asyncio
    async def test_choose_model_registers_escape_handler(self) -> None:
        key_bindings = Mock()
        callbacks = []

        def register(*args: object, **kwargs: object):
            del args, kwargs

            def decorator(callback):
                callbacks.append(callback)
                return callback

            return decorator

        key_bindings.add.side_effect = register
        event = Mock()
        with (
            patch("fragile.commands.interactive.commands.model.KeyBindings", return_value=key_bindings),
            patch(
                "fragile.commands.interactive.commands.model.select_history",
                new_callable=AsyncMock,
                return_value=(ModelType.OPENAI, "gpt"),
            ),
        ):
            assert await choose_model([((ModelType.OPENAI, "gpt"), "OpenAI gpt")]) == (ModelType.OPENAI, "gpt")

        callbacks[0](event)
        event.app.exit.assert_called_once()
        assert isinstance(event.app.exit.call_args.kwargs["exception"], click.Abort)

    @pytest.mark.asyncio
    async def test_handle_returns_continue_without_account(self, capsys) -> None:
        with patch(
            "fragile.commands.interactive.commands.model.Account.get_credentials",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await ModelCommand().handle(None, SessionState(thread_id=UUID(int=1)))

        assert result is CommandResult.CONTINUE
        assert "Configure an account" in capsys.readouterr().out

    @pytest.mark.asyncio
    async def test_discover_models_for_ollama(self) -> None:
        client = Mock()
        client.get = AsyncMock(
            return_value=Mock(json=Mock(return_value={"models": [{"name": "qwen"}]}), raise_for_status=Mock())
        )
        async_client = MagicMock(__aenter__=AsyncMock(return_value=client), __aexit__=AsyncMock(return_value=None))

        with patch("fragile.commands.interactive.commands.model.httpx.AsyncClient", return_value=async_client):
            models = await discover_models(ModelType.OLLAMA, "unused", "http://ollama.test/")

        assert models == ["qwen"]
        client.get.assert_awaited_once_with("http://ollama.test/api/tags", headers={})

    @pytest.mark.asyncio
    async def test_discover_models_for_openai(self) -> None:
        client = Mock()
        client.get = AsyncMock(
            return_value=Mock(json=Mock(return_value={"data": [{"id": "gpt-5"}]}), raise_for_status=Mock())
        )
        async_client = MagicMock(__aenter__=AsyncMock(return_value=client), __aexit__=AsyncMock(return_value=None))

        with patch("fragile.commands.interactive.commands.model.httpx.AsyncClient", return_value=async_client):
            models = await discover_models(ModelType.OPENAI, "secret", "https://openai.test")

        assert models == ["gpt-5"]
        client.get.assert_awaited_once_with("https://openai.test/models", headers={"Authorization": "Bearer secret"})

    @pytest.mark.asyncio
    async def test_discover_models_for_anthropic_paginates(self) -> None:
        client = Mock()
        client.get = AsyncMock(
            side_effect=[
                Mock(
                    json=Mock(return_value={"data": [{"id": "claude-1"}], "has_more": True, "last_id": "claude-1"}),
                    raise_for_status=Mock(),
                ),
                Mock(
                    json=Mock(return_value={"data": [{"id": "claude-2"}], "has_more": False}),
                    raise_for_status=Mock(),
                ),
            ]
        )
        async_client = MagicMock(__aenter__=AsyncMock(return_value=client), __aexit__=AsyncMock(return_value=None))

        with patch("fragile.commands.interactive.commands.model.httpx.AsyncClient", return_value=async_client):
            models = await discover_models(ModelType.ANTHROPIC, "secret", "https://anthropic.test/")

        assert models == ["claude-1", "claude-2"]
        assert client.get.await_args_list == [
            call(
                "https://anthropic.test/v1/models",
                headers={"anthropic-version": ANTHROPIC_VERSION, "x-api-key": "secret"},
                params={"limit": 100},
            ),
            call(
                "https://anthropic.test/v1/models",
                headers={"anthropic-version": ANTHROPIC_VERSION, "x-api-key": "secret"},
                params={"limit": 100, "after_id": "claude-1"},
            ),
        ]

    @pytest.mark.asyncio
    async def test_discover_models_returns_none_for_failed_or_invalid_response(self) -> None:
        client = Mock()
        client.get = AsyncMock(return_value=Mock(json=Mock(return_value={"data": [{}]}), raise_for_status=Mock()))
        async_client = MagicMock(__aenter__=AsyncMock(return_value=client), __aexit__=AsyncMock(return_value=None))

        with patch("fragile.commands.interactive.commands.model.httpx.AsyncClient", return_value=async_client):
            assert await discover_models(ModelType.OPENAI, "secret", "https://openai.test") is None

    @pytest.mark.asyncio
    async def test_discover_models_returns_none_when_request_fails(self) -> None:
        client = Mock()
        client.get = AsyncMock(side_effect=httpx.ConnectError("unavailable"))
        async_client = MagicMock(__aenter__=AsyncMock(return_value=client), __aexit__=AsyncMock(return_value=None))

        with patch("fragile.commands.interactive.commands.model.httpx.AsyncClient", return_value=async_client):
            assert await discover_models(ModelType.OPENAI, "secret", "https://openai.test") is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload",
        [
            {"data": [], "has_more": "yes"},
            {"data": [], "has_more": True},
            {"data": [{}], "has_more": False},
        ],
    )
    async def test_discover_models_rejects_invalid_anthropic_pagination(self, payload: dict[str, object]) -> None:
        client = Mock()
        client.get = AsyncMock(return_value=Mock(json=Mock(return_value=payload), raise_for_status=Mock()))
        async_client = MagicMock(__aenter__=AsyncMock(return_value=client), __aexit__=AsyncMock(return_value=None))

        with patch("fragile.commands.interactive.commands.model.httpx.AsyncClient", return_value=async_client):
            assert await discover_models(ModelType.ANTHROPIC, "secret", "https://anthropic.test") is None

    @pytest.mark.asyncio
    async def test_handle_returns_continue_when_discovery_fails(self, capsys) -> None:
        with (
            patch(
                "fragile.commands.interactive.commands.model.Account.get_credentials",
                new_callable=AsyncMock,
                return_value=("openai", "key", "https://example.com"),
            ),
            patch(
                "fragile.commands.interactive.commands.model.discover_models",
                new_callable=AsyncMock,
                return_value=None,
            ),
            patch(
                "fragile.commands.interactive.commands.model.Account.save_model_selection",
                new_callable=AsyncMock,
            ) as save,
        ):
            result = await ModelCommand().handle(None, SessionState(thread_id=UUID(int=1)))

        assert result is CommandResult.CONTINUE
        assert "Could not retrieve models" in capsys.readouterr().out
        save.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_handle_returns_continue_for_an_unsupported_provider(self) -> None:
        with patch(
            "fragile.commands.interactive.commands.model.Account.get_credentials",
            new_callable=AsyncMock,
            return_value=("unsupported", "key", "https://example.com"),
        ):
            result = await ModelCommand().handle(None, SessionState(thread_id=UUID(int=1)))

        assert result is CommandResult.CONTINUE

    @pytest.mark.asyncio
    async def test_handle_ignores_empty_cancelled_or_unchanged_selection(self) -> None:
        command = ModelCommand()
        state = SessionState(thread_id=UUID(int=1))
        with (
            patch(
                "fragile.commands.interactive.commands.model.Account.get_credentials",
                new_callable=AsyncMock,
                return_value=("openai", "key", "https://example.com"),
            ),
            patch.object(
                command,
                "_current_selection",
                new_callable=AsyncMock,
                return_value=(ModelType.OPENAI, "gpt-5"),
            ),
            patch(
                "fragile.commands.interactive.commands.model.discover_models",
                new_callable=AsyncMock,
                side_effect=[[], ["gpt-5"], ["gpt-5"]],
            ),
            patch(
                "fragile.commands.interactive.commands.model.choose_model",
                new_callable=AsyncMock,
                side_effect=[None, None, (ModelType.OPENAI, "gpt-5")],
            ),
            patch(
                "fragile.commands.interactive.commands.model.Account.save_model_selection",
                new_callable=AsyncMock,
            ) as save,
        ):
            assert await command.handle(None, state) is CommandResult.CONTINUE
            assert await command.handle(None, state) is CommandResult.CONTINUE
            assert await command.handle(None, state) is CommandResult.CONTINUE

        save.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_handle_persists_changed_selection(self) -> None:
        command = ModelCommand()
        with (
            patch(
                "fragile.commands.interactive.commands.model.Account.get_credentials",
                new_callable=AsyncMock,
                return_value=("openai", "key", "https://example.com"),
            ),
            patch.object(
                command,
                "_current_selection",
                new_callable=AsyncMock,
                return_value=(ModelType.OPENAI, "gpt-4o-mini"),
            ),
            patch(
                "fragile.commands.interactive.commands.model.discover_models",
                new_callable=AsyncMock,
                return_value=["gpt-4o-mini", "gpt-5"],
            ),
            patch(
                "fragile.commands.interactive.commands.model.choose_model",
                new_callable=AsyncMock,
                return_value=(ModelType.OPENAI, "gpt-5"),
            ),
            patch(
                "fragile.commands.interactive.commands.model.Account.save_model_selection",
                new_callable=AsyncMock,
            ) as save,
        ):
            result = await command.handle(None, SessionState(thread_id=UUID(int=1)))

        assert result is CommandResult.MODEL_CHANGED
        save.assert_awaited_once_with(ModelType.OPENAI, "gpt-5")

    @pytest.mark.asyncio
    async def test_handle_returns_continue_when_saving_fails(self) -> None:
        command = ModelCommand()
        with (
            patch(
                "fragile.commands.interactive.commands.model.Account.get_credentials",
                new_callable=AsyncMock,
                return_value=("openai", "key", "https://example.com"),
            ),
            patch.object(
                command,
                "_current_selection",
                new_callable=AsyncMock,
                return_value=(ModelType.OPENAI, "gpt-4o-mini"),
            ),
            patch(
                "fragile.commands.interactive.commands.model.discover_models",
                new_callable=AsyncMock,
                return_value=["gpt-5"],
            ),
            patch(
                "fragile.commands.interactive.commands.model.choose_model",
                new_callable=AsyncMock,
                return_value=(ModelType.OPENAI, "gpt-5"),
            ),
            patch(
                "fragile.commands.interactive.commands.model.Account.save_model_selection",
                new_callable=AsyncMock,
                side_effect=InvalidAccountError("invalid"),
            ),
        ):
            result = await command.handle(None, SessionState(thread_id=UUID(int=1)))

        assert result is CommandResult.CONTINUE

    @pytest.mark.asyncio
    async def test_current_selection_returns_provider_default_without_saved_selection(self) -> None:
        with patch(
            "fragile.commands.interactive.commands.model.Account.get_model_selection",
            new_callable=AsyncMock,
            return_value=None,
        ):
            selection = await ModelCommand._current_selection(ModelType.OPENAI)

        assert selection[0] is ModelType.OPENAI

    @pytest.mark.asyncio
    async def test_current_selection_returns_saved_selection_for_provider(self) -> None:
        with patch(
            "fragile.commands.interactive.commands.model.Account.get_model_selection",
            new_callable=AsyncMock,
            return_value=("openai", "gpt-5"),
        ):
            selection = await ModelCommand._current_selection(ModelType.OPENAI)

        assert selection == (ModelType.OPENAI, "gpt-5")
