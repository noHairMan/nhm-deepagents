"""Prompt-toolkit input handling."""

from collections.abc import Callable, Iterator
from typing import Any

from prompt_toolkit import PromptSession
from prompt_toolkit.application import get_app
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.output import Output
from prompt_toolkit.styles import Style

from fragile.commands.interactive.commands import command_registry

PROMPT_STYLE = Style.from_dict({"prompt": "#00aa00 bold"})
TOOLBAR_FALLBACK = "unknown"
TOOLBAR_MAX_WIDTH = 120


def _single_line(value: object, default: str = TOOLBAR_FALLBACK) -> str:
    text = str(value or default).replace("\r", " ").replace("\n", " ").strip()
    return text or default


def _toolbar_width(output: Output | None) -> int:
    active_output = output or get_app().output
    try:
        return max(1, active_output.get_size().columns)
    except AttributeError, OSError:
        return TOOLBAR_MAX_WIDTH


def format_toolbar(
    thread_id: str | None = None,
    output: Output | None = None,
    model_provider: object = None,
    model: object = None,
) -> str:
    """Return a safe, single-line summary for the interactive prompt toolbar."""
    provider = _single_line(model_provider)
    model_name = _single_line(model)
    thread = _single_line(thread_id)
    toolbar = f"Model: {provider}/{model_name} | Thread: {thread}"
    width = _toolbar_width(output)
    if len(toolbar) <= width:
        return toolbar
    return f"{toolbar[: max(0, width - 1)].rstrip()}…"


def create_toolbar(
    thread_id: str | None = None,
    output: Output | None = None,
    model_provider: Callable[[], object] | None = None,
    model: Callable[[], object] | None = None,
) -> Callable[[], str]:
    """Create a dynamic toolbar callback that reads Fragile's model context on each render."""
    return lambda: format_toolbar(
        thread_id,
        output,
        model_provider() if model_provider is not None else None,
        model() if model is not None else None,
    )


def clear_submitted_input(output: Output, user_input: str) -> None:
    """Erase a submitted prompt from the active terminal screen."""
    line_count = max(1, user_input.count("\n") + 1)
    sequences = ["\r\033[2K"]
    sequences.extend("\033[1A\r\033[2K" for _ in range(line_count - 1))
    output.write_raw("".join(sequences))
    output.flush()


def clear_submitted_input_after_interaction(output: Output, user_input: str) -> None:
    """Erase a prompt after a nested full-screen interaction has returned."""
    line_count = max(1, user_input.count("\n") + 1)
    sequences = ["\r\033[2K"]
    sequences.extend("\033[1A\r\033[2K" for _ in range(line_count))
    output.write_raw("".join(sequences))
    output.flush()


class CommandCompleter(Completer):
    """补全 Fragile 的内置斜杠命令。"""

    def get_completions(self, document: object, complete_event: object) -> Iterator[Completion]:
        text_before_cursor = getattr(document, "text_before_cursor", "")
        if not text_before_cursor.startswith("/") or " " in text_before_cursor:
            return
        for command in (f"/{handler.name}" for handler in command_registry.handlers):
            if command.startswith(text_before_cursor):
                yield Completion(command, start_position=-len(text_before_cursor))


def create_prompt_session(
    output: Output | None = None,
    thread_id: str | None = None,
    model_provider: Callable[[], object] | None = None,
    model: Callable[[], object] | None = None,
) -> PromptSession[str]:
    key_bindings = KeyBindings()

    @key_bindings.add("enter")
    def submit(event: Any) -> None:
        event.current_buffer.validate_and_handle()

    @key_bindings.add("escape", "enter")
    def insert_newline(event: Any) -> None:
        event.current_buffer.insert_text("\n")

    return PromptSession(
        history=InMemoryHistory(),
        completer=CommandCompleter(),
        style=PROMPT_STYLE,
        multiline=True,
        enable_suspend=True,
        key_bindings=key_bindings,
        output=output,
        bottom_toolbar=create_toolbar(thread_id, output, model_provider, model),
    )
