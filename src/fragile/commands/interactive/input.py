"""Prompt-toolkit input handling."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from fragile.commands.enums import Command

PROMPT_STYLE = Style.from_dict({"prompt": "#00aa00 bold"})
COMMANDS = tuple(f"/{command.value}" for command in Command)


class CommandCompleter(Completer):
    """补全 Fragile 的内置斜杠命令。"""

    def get_completions(self, document: object, complete_event: object) -> Iterator[Completion]:
        text_before_cursor = getattr(document, "text_before_cursor", "")
        if not text_before_cursor.startswith("/") or " " in text_before_cursor:
            return
        for command in COMMANDS:
            if command.startswith(text_before_cursor):
                yield Completion(command, start_position=-len(text_before_cursor))


def create_prompt_session() -> PromptSession[str]:
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
    )


def prompt(session: PromptSession[str]) -> str:
    """读取一条支持历史、补全和多行编辑的用户输入。"""
    return session.prompt("你> ")
