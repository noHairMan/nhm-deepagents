from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
import typer
from typer.testing import CliRunner

from fragile.cli import app
from fragile.exceptions import FragileError, InvalidThreadIdError

runner = CliRunner()


class TestApp:
    @pytest.mark.asyncio
    async def test_events_filters_and_yields_text(self) -> None:
        agent = MagicMock()

        async def stream(*args, **kwargs):
            yield "ignored"
            yield {"event": "other", "data": {}}
            yield {"event": "on_chat_model_stream", "data": {"chunk": MagicMock(content="")}}
            yield {"event": "on_chat_model_stream", "data": {"chunk": MagicMock(content="ok")}}
            yield {
                "event": "on_chat_model_stream",
                "data": {
                    "chunk": MagicMock(content=[{"type": "text", "text": "你好"}, {"type": "text", "text": "呀"}])
                },
            }

        agent.astream_events = stream
        from fragile.commands.interactive import _events

        assert [value async for value in _events(agent, "prompt", UUID(int=1))] == ["ok", "你好呀"]

    def test_content_text_handles_supported_content(self) -> None:
        from fragile.commands.interactive import _content_text

        assert _content_text("text") == "text"
        assert _content_text(["a", {"type": "text", "text": "b"}, {"type": "image"}]) == "ab"
        assert _content_text(None) == ""

    def test_is_exit_command_ignores_case_and_whitespace(self) -> None:
        from fragile.commands.interactive import _is_exit_command

        assert _is_exit_command("  EXIT  ") is True
        assert _is_exit_command("continue") is False

    @pytest.mark.asyncio
    async def test_chat_uses_checkpoint_and_prints(self, capsys) -> None:
        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value="checkpoint")
        context.__aexit__ = AsyncMock(return_value=None)
        with (
            patch("fragile.commands.interactive.get_checkpointer_context", return_value=context),
            patch("fragile.commands.interactive.AgentManager.create_agent", return_value=MagicMock()),
            patch("fragile.commands.interactive._events", return_value=self._async_values("answer")),
        ):
            from fragile.commands.interactive import _chat

            await _chat("prompt", UUID(int=1))
        assert capsys.readouterr().out == "answer\n"

    @staticmethod
    async def _async_values(*values: str):
        for value in values:
            yield value

    def test_help(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "interactive" not in result.stdout

    def test_prompt_argument_is_rejected(self) -> None:
        result = runner.invoke(app, ["你好"])
        assert result.exit_code != 0

    def test_invalid_thread(self) -> None:
        result = runner.invoke(app, ["--thread", "bad"])
        assert result.exit_code != 0

    def test_thread_id_rejects_invalid_value(self) -> None:
        from fragile.commands.interactive import _thread_id

        with pytest.raises(InvalidThreadIdError, match="必须是有效的 UUID"):
            _thread_id("bad")

    def test_invalid_thread_id_is_fragile_error_and_typer_parameter(self) -> None:
        assert issubclass(InvalidThreadIdError, FragileError)
        assert issubclass(InvalidThreadIdError, typer.BadParameter)

    def test_main_without_prompt(self) -> None:
        from fragile.cli import main

        with patch("fragile.cli.interactive") as interactive:
            main(None)
        interactive.assert_called_once_with(None)

    def test_main_without_arguments_enters_interactive_mode(self) -> None:
        with patch("fragile.commands.interactive._chat", new_callable=AsyncMock) as chat:
            result = runner.invoke(app, [], input="exit\n")
        assert result.exit_code == 0
        chat.assert_not_awaited()

    def test_interactive_handles_keyboard_interrupt(self) -> None:
        from fragile.commands.interactive import interactive

        with patch("fragile.commands.interactive.typer.prompt", side_effect=KeyboardInterrupt):
            interactive(None)

    def test_interactive_sends_nonempty_prompt(self) -> None:
        from fragile.commands.interactive import interactive

        with (
            patch("fragile.commands.interactive.typer.prompt", side_effect=["hello", "quit"]),
            patch("fragile.commands.interactive._chat", new_callable=AsyncMock) as chat,
        ):
            interactive(None)
        chat.assert_awaited_once()

    def test_interactive_empty_prompt(self) -> None:
        with patch("fragile.commands.interactive._chat", new_callable=AsyncMock):
            result = runner.invoke(app, [], input="\nexit\n")
        assert result.exit_code == 0

    def test_thread_id(self) -> None:
        from fragile.commands.interactive import _thread_id

        value = UUID("12345678-1234-5678-1234-567812345678")
        assert _thread_id(str(value)) == value
