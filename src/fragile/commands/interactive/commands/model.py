"""Model selection command handling."""

import logging
from typing import Any

import asyncclick as click
import httpx
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from fragile.commands.interactive.commands.base import Command as BaseCommand
from fragile.commands.interactive.commands.history import select_history
from fragile.models import Account, InvalidAccountError, SessionState
from fragile.models.constants import CommandResult
from tomorrow.conf import settings as tomorrow_settings
from tomorrow.models.constants import ModelType

logger = logging.getLogger(__name__)

MODEL_STYLE = Style.from_dict({"selected-option": "fg:ansigreen bold"})
ModelSelection = tuple[ModelType, str]
ANTHROPIC_VERSION = "2023-06-01"


def _provider_url(base_url: str, path: str) -> str:
    """Append a provider endpoint path to the configured base URL."""
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def _response_model_names(response: object, key: str) -> list[str] | None:
    """Extract non-empty model names from a provider response collection."""
    if not isinstance(response, dict):
        return None
    models = response.get(key)
    if not isinstance(models, list):
        return None
    names: list[str] = []
    for model in models:
        if not isinstance(model, dict):
            return None
        name = model.get("name") if key == "models" else model.get("id")
        if not isinstance(name, str) or not name.strip():
            return None
        names.append(name.strip())
    return names


async def discover_models(provider: ModelType, api_key: str, base_url: str) -> list[str] | None:
    """Return models exposed by the configured provider, or ``None`` on failure."""
    headers: dict[str, str] = {}
    path: str
    response_key: str
    if provider is ModelType.OLLAMA:
        path = "/api/tags"
        response_key = "models"
    elif provider is ModelType.OPENAI:
        path = "/models"
        response_key = "data"
        headers["Authorization"] = f"Bearer {api_key}"
    else:
        path = "/v1/models"
        response_key = "data"
        headers = {"anthropic-version": ANTHROPIC_VERSION, "x-api-key": api_key}

    try:
        async with httpx.AsyncClient() as client:
            if provider is not ModelType.ANTHROPIC:
                response = await client.get(_provider_url(base_url, path), headers=headers)
                response.raise_for_status()
                names = _response_model_names(response.json(), response_key)
                if names is None:
                    raise ValueError("response has an invalid model list")
                return names

            names = []
            params: dict[str, int | str] = {"limit": 100}
            while True:
                response = await client.get(_provider_url(base_url, path), headers=headers, params=params.copy())
                response.raise_for_status()
                payload = response.json()
                page_names = _response_model_names(payload, response_key)
                if page_names is None:
                    raise ValueError("response has an invalid model list")
                names.extend(page_names)
                has_more = payload.get("has_more", False)
                if not isinstance(has_more, bool):
                    raise ValueError("response has an invalid has_more value")
                if not has_more:
                    return names
                last_id = payload.get("last_id")
                if not isinstance(last_id, str) or not last_id.strip():
                    raise ValueError("paginated response is missing last_id")
                params["after_id"] = last_id
    except (httpx.HTTPError, ValueError, TypeError) as error:
        logger.warning("Could not discover %s models from %s: %s", provider.value, base_url, error)
        return None


def build_model_options(
    catalog: dict[ModelType, tuple[str, ...]], current: ModelSelection | None
) -> list[tuple[ModelSelection, str]]:
    """Build provider-grouped labels for the discovered model catalog."""
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
        click.echo("No models are available for the current account.")
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
        provider_name, api_key, base_url = credentials
        try:
            provider = ModelType(provider_name.strip().lower())
        except ValueError:
            logger.exception("Configured account has an unsupported provider: %s", provider_name)
            return CommandResult.CONTINUE
        current = await self._current_selection(provider)
        model_names = await discover_models(provider, api_key, base_url)
        if model_names is None:
            click.echo("Could not retrieve models for the current account.")
            return CommandResult.CONTINUE
        options = build_model_options({provider: tuple(model_names)}, current)
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
