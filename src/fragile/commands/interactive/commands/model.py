"""Model selection command handling."""

import logging
from dataclasses import dataclass
from typing import Any

import asyncclick as click
import httpx
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.layout import HSplit, Layout
from prompt_toolkit.output import Output
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Label, RadioList

from fragile.commands.interactive.commands.base import Command as BaseCommand
from fragile.models import Account, InvalidAccountError, SessionState
from fragile.models.constants import CommandResult
from tomorrow.conf import settings as tomorrow_settings
from tomorrow.models.constants import ModelType

logger = logging.getLogger(__name__)

MODEL_STYLE = Style.from_dict({"selected-option": "fg:ansigreen bold"})
ModelSelection = tuple[ModelType, str]
ANTHROPIC_VERSION = "2023-06-01"


@dataclass(frozen=True)
class ModelRecord:
    """A validated provider model and its available display metadata."""

    provider: ModelType
    model_id: str
    details: tuple[tuple[str, str], ...] = ()


def _provider_url(base_url: str, path: str) -> str:
    """Append a provider endpoint path to the configured base URL."""
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def _optional_text(model: dict[str, object], key: str, label: str) -> tuple[str, str] | None:
    """Return a non-empty text metadata field, if present."""
    value = model.get(key)
    if isinstance(value, str) and value.strip():
        return label, value.strip()
    return None


def _optional_integer(model: dict[str, object], key: str, label: str) -> tuple[str, str] | None:
    """Return an integer metadata field, if present."""
    value = model.get(key)
    if isinstance(value, int) and not isinstance(value, bool):
        return label, str(value)
    return None


def _ollama_details(model: dict[str, object]) -> tuple[tuple[str, str], ...]:
    """Extract displayable metadata from an Ollama model."""
    details = [
        _optional_integer(model, "size", "Size (bytes)"),
        _optional_text(model, "modified_at", "Modified at"),
    ]
    nested_details = model.get("details")
    if isinstance(nested_details, dict):
        details.extend(
            [
                _optional_text(nested_details, "parameter_size", "Parameter size"),
                _optional_text(nested_details, "quantization_level", "Quantization"),
                _optional_text(nested_details, "family", "Family"),
            ]
        )
    return tuple(detail for detail in details if detail is not None)


def _record_details(provider: ModelType, model: dict[str, object]) -> tuple[tuple[str, str], ...]:
    """Extract validated provider-specific metadata for a model."""
    if provider is ModelType.OLLAMA:
        return _ollama_details(model)
    if provider is ModelType.OPENAI:
        details = [_optional_text(model, "owned_by", "Owner"), _optional_integer(model, "created", "Created")]
    else:
        details = [
            _optional_text(model, "display_name", "Display name"),
            _optional_text(model, "created_at", "Created at"),
            _optional_integer(model, "context_window", "Input context"),
            _optional_integer(model, "max_tokens", "Maximum output tokens"),
        ]
    return tuple(detail for detail in details if detail is not None)


def _response_model_records(response: object, key: str, provider: ModelType) -> list[ModelRecord] | None:
    """Extract validated model records from a provider response collection."""
    if not isinstance(response, dict):
        return None
    models = response.get(key)
    if not isinstance(models, list):
        return None
    records: list[ModelRecord] = []
    for model in models:
        if not isinstance(model, dict):
            return None
        model_id = model.get("name") if provider is ModelType.OLLAMA else model.get("id")
        if not isinstance(model_id, str) or not model_id.strip():
            return None
        records.append(ModelRecord(provider, model_id.strip(), _record_details(provider, model)))
    return records


async def discover_models(provider: ModelType, api_key: str, base_url: str) -> list[ModelRecord] | None:
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
                records = _response_model_records(response.json(), response_key, provider)
                if records is None:
                    raise ValueError("response has an invalid model list")
                return records

            records = []
            params: dict[str, int | str] = {"limit": 100}
            while True:
                response = await client.get(_provider_url(base_url, path), headers=headers, params=params.copy())
                response.raise_for_status()
                payload = response.json()
                page_records = _response_model_records(payload, response_key, provider)
                if page_records is None:
                    raise ValueError("response has an invalid model list")
                records.extend(page_records)
                has_more = payload.get("has_more", False)
                if not isinstance(has_more, bool):
                    raise ValueError("response has an invalid has_more value")
                if not has_more:
                    return records
                last_id = payload.get("last_id")
                if not isinstance(last_id, str) or not last_id.strip():
                    raise ValueError("paginated response is missing last_id")
                params["after_id"] = last_id
    except (httpx.HTTPError, ValueError, TypeError) as error:
        logger.warning("Could not discover %s models from %s: %s", provider.value, base_url, error)
        return None


def build_model_options(
    catalog: dict[ModelType, tuple[ModelRecord, ...]], current: ModelSelection | None
) -> list[tuple[ModelSelection, str]]:
    """Build provider-grouped labels for the discovered model catalog."""
    options: list[tuple[ModelSelection, str]] = []
    for provider in ModelType:
        for model in catalog.get(provider, ()):
            selection = provider, model.model_id
            current_marker = "  Current model" if selection == current else ""
            options.append((selection, f"{provider.label:<10} {model.model_id}{current_marker}"))
    return options


def format_model_details(record: ModelRecord | None) -> str:
    """Format the details panel for the currently highlighted model."""
    if record is None:
        return ""
    lines = ["Model details", f"Provider: {record.provider.label}", f"Model ID: {record.model_id}"]
    lines.extend(f"{label}: {value}" for label, value in record.details)
    return "\n".join(lines)


def build_model_application(
    records: list[ModelRecord],
    current: ModelSelection | None,
    key_bindings: KeyBindings,
    output: Output | None = None,
) -> tuple[Application, RadioList]:
    """Build the full-screen model selector with a dynamic details panel."""
    catalog = {provider: tuple(record for record in records if record.provider is provider) for provider in ModelType}
    options = build_model_options(catalog, current)
    records_by_selection = {(record.provider, record.model_id): record for record in records}
    radio_list = RadioList(
        values=options,
        select_on_focus=True,
        open_character="",
        select_character="",
        close_character="",
        show_cursor=False,
        show_numbers=False,
        container_style="class:input-selection",
        default_style="class:option",
        selected_style="",
        checked_style="class:selected-option",
        number_style="class:number",
        show_scrollbar=False,
    )
    bindings = KeyBindings()

    @bindings.add("enter", eager=True)
    def accept_selection(event: Any) -> None:
        event.app.exit(result=radio_list.current_value)

    application = Application(
        layout=Layout(
            HSplit(
                [
                    Label("Select a model (Enter confirms, Esc cancels):", dont_extend_height=True),
                    radio_list,
                    Label("", dont_extend_height=True),
                    Label(lambda: format_model_details(records_by_selection.get(radio_list.current_value))),
                ]
            ),
            focused_element=radio_list,
        ),
        key_bindings=merge_key_bindings([bindings, key_bindings]),
        style=MODEL_STYLE,
        full_screen=True,
        output=output,
    )
    return application, radio_list


async def choose_model(records: list[ModelRecord], current: ModelSelection | None) -> ModelSelection | None:
    """Display the full-screen model selector and return the chosen model."""
    if not records:
        click.echo("No models are available for the current account.")
        return None
    key_bindings = KeyBindings()

    @key_bindings.add("escape", eager=True)
    def cancel_selection(event: Any) -> None:
        event.app.exit(exception=click.Abort())

    try:
        application, _ = build_model_application(records, current, key_bindings)
        return await application.run_async()
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
        models = await discover_models(provider, api_key, base_url)
        if models is None:
            click.echo("Could not retrieve models for the current account.")
            return CommandResult.CONTINUE
        selected = await choose_model(models, current)
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
