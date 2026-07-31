import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from asyncclick.testing import CliRunner

from fragile.app import app

runner = CliRunner()


class TestCli:
    @pytest.mark.asyncio
    async def test_help(self) -> None:
        result = await runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "interactive" not in result.stdout

    @pytest.mark.asyncio
    async def testprompt_argument_is_rejected(self) -> None:
        result = await runner.invoke(app, ["你好"])
        assert result.exit_code != 0

    @pytest.mark.asyncio
    async def test_invalid_thread(self) -> None:
        result = await runner.invoke(app, ["--thread", "bad"])
        assert result.exit_code != 0

    def test_main_without_prompt(self) -> None:
        from fragile.app import main

        with patch("fragile.app.interactive", new_callable=AsyncMock) as interactive:
            asyncio.run(main(None, None))
        interactive.assert_called_once_with(None)

    def test_main_runs_async_interactive_session(self) -> None:
        from fragile.app import main

        with patch("fragile.app.interactive", new_callable=AsyncMock) as interactive:
            asyncio.run(main(None, None))
        interactive.assert_called_once_with(None)

    def test_main_skips_interactive_when_subcommand_is_invoked(self) -> None:
        from fragile.app import main

        context = type("Context", (), {"invoked_subcommand": "purge"})()
        with patch("fragile.app.interactive") as interactive:
            asyncio.run(main(context, None))
        interactive.assert_not_called()

    def test_main_starts_interactive_without_subcommand(self) -> None:
        from fragile.app import main

        context = type("Context", (), {"invoked_subcommand": None})()
        with (
            patch("fragile.app.interactive", new_callable=AsyncMock) as interactive,
        ):
            asyncio.run(main(context, "thread-id"))
        interactive.assert_called_once_with("thread-id")

    @pytest.mark.asyncio
    async def test_purge_command(self) -> None:
        with patch("fragile.app.purge_sessions", new_callable=AsyncMock, return_value=3) as purge_sessions:
            result = await runner.invoke(app, ["purge"])
        assert result.exit_code == 0
        assert result.stdout == "Cleared 3 session records.\n"
        purge_sessions.assert_called_once_with()
