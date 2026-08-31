"""Model selection command handling."""

import logging
from typing import Any

import asyncclick as click
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from fragile.commands.interactive.commands.base import Command as BaseCommand
from fragile.commands.interactive.commands.history import select_history
from fragile.conf import settings
from fragile.models import Account, InvalidAccountError, SessionState
from fragile.models.constants import CommandResult
from tomorrow.conf import settings as tomorrow_settings
from tomorrow.models.constants import ModelType

logger = logging.getLogger(__name__)

MODEL_STYLE = Style.from_dict({"selected-option": "fg:ansigreen bold"})
ModelSelection = tuple[ModelType, str]


def build_model_options(
    catalog: dict[ModelType, tuple[str, ...]], current: ModelSelection | None
) -> list[tuple[ModelSelection, str]]:
    """Build provider-grouped labels for the configured model catalog."""
    options: list[tuple[ModelSelection, str]] = []
    for provider in ModelType:
        for model in catalog.get(provider, ()):
            selection = provider, model
            current_marker = "  Current model" if selection == current else ""
            options.append((selection, f"{provider.label:<10} {model}{current_marker}"))
    return options


async def choose_model(options: list[tuple[ModelSelection, str]]) -> ModelSelection | None:
    """Display the full-screen model selector and return the chosen model."""
    if not options:
        click.echo("No configured models are available for the current account.")
        return None
    key_bindings = KeyBindings()

    @key_bindings.add("escape", eager=True)
    def cancel_selection(event: Any) -> None:
        event.app.exit(exception=click.Abort())

    try:
        return await select_history(
            "Select a model (Enter confirms, Esc cancels):",
            options=options,
            key_bindings=key_bindings,
            style=MODEL_STYLE,
            symbol="",
            enable_interrupt=False,
        )
    except click.Abort:
        return None


class ModelCommand(BaseCommand):
    """Select the model used by the configured external provider."""

    name = "model"

    async def handle(self, prompt: str | None, state: SessionState) -> CommandResult:
        """Persist a changed model selection for the configured account provider."""
        del prompt, state
        credentials = await Account.get_credentials()
        if credentials is None:
            click.echo("Configure an account with /account before selecting a model.")
            return CommandResult.CONTINUE
        provider_name, _, _ = credentials
        try:
            provider = ModelType(provider_name.strip().lower())
        except ValueError:
            logger.exception("Configured account has an unsupported provider: %s", provider_name)
            return CommandResult.CONTINUE
        current = await self._current_selection(provider)
        options = build_model_options({provider: settings.MODEL_CATALOG.get(provider, ())}, current)
        selected = await choose_model(options)
        if selected is None or selected == current:
            return CommandResult.CONTINUE
        try:
            await Account.save_model_selection(selected[0], selected[1])
        except InvalidAccountError as error:
            logger.exception("Model selection could not be saved: %s", error)
            return CommandResult.CONTINUE
        return CommandResult.MODEL_CHANGED

    @staticmethod
    async def _current_selection(provider: ModelType) -> ModelSelection:
        """Return the persisted selection or the provider's active default model."""
        selection = await Account.get_model_selection()
        if selection is not None and selection[0] == provider:
            return provider, selection[1]
        model_config = getattr(tomorrow_settings.MODEL, provider.value)
        return provider, model_config.model
