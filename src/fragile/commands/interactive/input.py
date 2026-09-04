"""Prompt-toolkit input handling."""

from collections.abc import Iterator
from typing import Any

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.output import Output
from prompt_toolkit.styles import Style

from fragile.commands.interactive.commands import command_registry

PROMPT_STYLE = Style.from_dict({"prompt": "#00aa00 bold"})


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


def create_prompt_session(output: Output | None = None) -> PromptSession[str]:
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
    )
