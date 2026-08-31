from unittest.mock import AsyncMock, MagicMock, Mock, call, patch
from uuid import UUID

import asyncclick as click
import httpx
import pytest
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.output import DummyOutput

from fragile.commands.interactive.commands.model import (
    ANTHROPIC_VERSION,
    ModelCommand,
    ModelRecord,
    _response_model_records,
    build_model_application,
    build_model_options,
    choose_model,
    discover_models,
    format_model_details,
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
    def test_response_model_records_rejects_invalid_collections(self, response: object, key: str) -> None:
        assert _response_model_records(response, key, ModelType.OLLAMA) is None

    @pytest.mark.parametrize(
        ("provider", "key", "response", "expected"),
        [
            (
                ModelType.OLLAMA,
                "models",
                {
                    "models": [
                        {
                            "name": "qwen",
                            "size": 1,
                            "modified_at": "2026-01-01T00:00:00Z",
                            "details": {"parameter_size": "7B", "quantization_level": "Q4", "family": "qwen"},
                        }
                    ]
                },
                (
                    ("Size (bytes)", "1"),
                    ("Modified at", "2026-01-01T00:00:00Z"),
                    ("Parameter size", "7B"),
                    ("Quantization", "Q4"),
                    ("Family", "qwen"),
                ),
            ),
            (
                ModelType.OPENAI,
                "data",
                {"data": [{"id": "gpt", "owned_by": "openai", "created": 1}]},
                (("Owner", "openai"), ("Created", "1")),
            ),
            (
                ModelType.ANTHROPIC,
                "data",
                {
                    "data": [
                        {
                            "id": "claude",
                            "display_name": "Claude",
                            "created_at": "2026-01-01",
                            "context_window": 200000,
                            "max_tokens": 8192,
                        }
                    ]
                },
                (
                    ("Display name", "Claude"),
                    ("Created at", "2026-01-01"),
                    ("Input context", "200000"),
                    ("Maximum output tokens", "8192"),
                ),
            ),
        ],
    )
    def test_response_model_records_keeps_valid_provider_metadata(
        self, provider: ModelType, key: str, response: object, expected: tuple[tuple[str, str], ...]
    ) -> None:
        assert _response_model_records(response, key, provider) == [
            ModelRecord(
                provider,
                {ModelType.OLLAMA: "qwen", ModelType.OPENAI: "gpt", ModelType.ANTHROPIC: "claude"}[provider],
                expected,
            )
        ]

    def test_response_model_records_omits_missing_or_invalid_optional_metadata(self) -> None:
        response = {"data": [{"id": "gpt", "owned_by": 1, "created": True}]}

        assert _response_model_records(response, "data", ModelType.OPENAI) == [ModelRecord(ModelType.OPENAI, "gpt")]

    def test_format_model_details_omits_unavailable_record(self) -> None:
        assert format_model_details(None) == ""

    def test_build_model_options_groups_providers_and_marks_current_model(self) -> None:
        options = build_model_options(
            {
                ModelType.ANTHROPIC: (ModelRecord(ModelType.ANTHROPIC, "claude"),),
                ModelType.OPENAI: (ModelRecord(ModelType.OPENAI, "gpt"),),
            },
            (ModelType.OPENAI, "gpt"),
        )

        assert options == [
            ((ModelType.ANTHROPIC, "claude"), "Anthropic  claude"),
            ((ModelType.OPENAI, "gpt"), "OpenAI     gpt  Current model"),
        ]

    @pytest.mark.asyncio
    async def test_choose_model_returns_none_for_empty_options(self, capsys) -> None:
        assert await choose_model([], None) is None
        assert "No models are available" in capsys.readouterr().out

    @pytest.mark.asyncio
    async def test_choose_model_returns_none_when_cancelled(self) -> None:
        application = MagicMock()
        application.run_async = AsyncMock(side_effect=click.Abort())
        with patch(
            "fragile.commands.interactive.commands.model.build_model_application",
            return_value=(application, MagicMock()),
        ):
            assert await choose_model([ModelRecord(ModelType.OPENAI, "gpt")], None) is None

    def test_model_application_accepts_selection_and_updates_details(self) -> None:
        first = ModelRecord(ModelType.OPENAI, "gpt", (("Owner", "openai"),))
        second = ModelRecord(ModelType.ANTHROPIC, "claude", (("Display name", "Claude"),))
        application, radio_list = build_model_application([first, second], None, KeyBindings(), output=DummyOutput())
        event = MagicMock()
        event.app = MagicMock()

        assert application.full_screen is True
        assert format_model_details(second) in application.layout.container.children[-1].content.text()()
        radio_list.current_value = (ModelType.OPENAI, "gpt")
        assert format_model_details(first) in application.layout.container.children[-1].content.text()()
        binding = next(
            binding for binding in application.key_bindings.bindings if binding.handler.__name__ == "accept_selection"
        )
        binding.handler(event)
        event.app.exit.assert_called_once_with(result=(ModelType.OPENAI, "gpt"))

    @pytest.mark.asyncio
    async def test_choose_model_registers_escape_handler(self) -> None:
        key_bindings = Mock()
        callbacks = []
        application = MagicMock()
        application.run_async = AsyncMock(return_value=(ModelType.OPENAI, "gpt"))

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
                "fragile.commands.interactive.commands.model.build_model_application",
                return_value=(application, MagicMock()),
            ),
        ):
            assert await choose_model([ModelRecord(ModelType.OPENAI, "gpt")], None) == (ModelType.OPENAI, "gpt")

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

        assert models == [ModelRecord(ModelType.OLLAMA, "qwen")]
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

        assert models == [ModelRecord(ModelType.OPENAI, "gpt-5")]
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

        assert models == [ModelRecord(ModelType.ANTHROPIC, "claude-1"), ModelRecord(ModelType.ANTHROPIC, "claude-2")]
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
                side_effect=[[], [ModelRecord(ModelType.OPENAI, "gpt-5")], [ModelRecord(ModelType.OPENAI, "gpt-5")]],
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
                return_value=[ModelRecord(ModelType.OPENAI, "gpt-4o-mini"), ModelRecord(ModelType.OPENAI, "gpt-5")],
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
                return_value=[ModelRecord(ModelType.OPENAI, "gpt-5")],
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
