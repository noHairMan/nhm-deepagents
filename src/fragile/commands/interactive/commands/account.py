"""Account configuration command handling."""

from typing import Any

import asyncclick as click
from prompt_toolkit import PromptSession
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Label, RadioList

from fragile.commands.interactive.commands.base import Command as BaseCommand
from fragile.models import Account, InvalidAccountError, SessionState
from fragile.models.constants import CommandResult
from tomorrow.models.constants import ModelType


class AccountCommand(BaseCommand):
    """Interactively persist credentials for an external model provider."""

    name = "account"
    providers: tuple[ModelType, ...] = tuple(ModelType)

    async def handle(self, prompt: str | None, state: SessionState) -> CommandResult:
        """Select a provider and interactively collect its credentials."""
        del prompt, state
        provider = await self._select_provider()
        if provider is None:
            return CommandResult.CONTINUE
        session = PromptSession()
        bindings = KeyBindings()

        @bindings.add("escape", eager=True)
        def cancel_credentials(event: Any) -> None:
            event.app.exit(exception=click.Abort())

        try:
            base_url = await session.prompt_async(f"{provider} base URL: ", key_bindings=bindings)
            api_key = await session.prompt_async(f"{provider} API key: ", is_password=True, key_bindings=bindings)
        except KeyboardInterrupt, EOFError, click.Abort:
            click.echo()
            return CommandResult.CONTINUE
        try:
            await Account.save_credentials(provider, api_key, base_url)
        except (InvalidAccountError, ValueError) as error:
            click.echo(f"Account not saved: {error}")
            return CommandResult.CONTINUE
        click.echo("Account settings saved.")
        return CommandResult.CONTINUE

    @staticmethod
    def _mask_api_key(api_key: str) -> str:
        """Mask an API key while retaining safe identifying fragments."""
        if len(api_key) <= 8:
            return "*" * 8
        return f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}"

    async def _current_account_text(self) -> str:
        """Return persisted account details without exposing the full API key."""
        credentials = await Account.get_credentials()
        if credentials is None:
            return ""
        saved_provider, api_key, base_url = credentials
        return f"Current account for {saved_provider}:\nBase URL: {base_url}\nAPI key: {self._mask_api_key(api_key)}"

    async def _select_provider(self) -> ModelType | None:
        """Display the provider selector and return the selected provider."""
        values = [(provider, provider.label) for provider in self.providers]
        radio_list = RadioList(values=values, select_on_focus=True, show_numbers=False)
        current_account = await self._current_account_text()
        bindings = KeyBindings()

        @bindings.add("enter", eager=True)
        def accept_selection(event: Any) -> None:
            event.app.exit(result=radio_list.current_value)

        @bindings.add("escape", eager=True)
        def cancel_selection(event: Any) -> None:
            event.app.exit(exception=click.Abort())

        application = Application(
            layout=Layout(
                HSplit(
                    [Label("Manage external LLM provider credentials"), radio_list, Label(""), Label(current_account)]
                ),
                focused_element=radio_list,
            ),
            key_bindings=bindings,
            style=Style.from_dict({"selected-option": "fg:ansigreen bold"}),
            full_screen=True,
        )
        try:
            return await application.run_async()
        except click.Abort:
            return None
