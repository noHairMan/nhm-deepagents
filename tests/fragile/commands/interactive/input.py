from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from prompt_toolkit.document import Document
from prompt_toolkit.keys import Keys
from prompt_toolkit.output import DummyOutput

from fragile.commands.interactive.input import (
    CommandCompleter,
    clear_submitted_input,
    clear_submitted_input_after_interaction,
    create_prompt_session,
)


class TestInput:
    def test_clear_submitted_input_erases_each_multiline_input_line(self) -> None:
        output = DummyOutput()

        clear_submitted_input(output, "first\nsecond")

    def test_clear_submitted_input_writes_cleanup_sequences(self) -> None:
        output = MagicMock()

        clear_submitted_input(output, "first\nsecond")

        output.write_raw.assert_called_once_with("\r\033[2K\033[1A\r\033[2K")
        output.flush.assert_called_once_with()

    def test_clear_submitted_input_after_interaction_clears_returned_screen_line(self) -> None:
        output = MagicMock()

        clear_submitted_input_after_interaction(output, "/history")

        output.write_raw.assert_called_once_with("\r\033[2K\033[1A\r\033[2K")
        output.flush.assert_called_once_with()

    def testprompt_session_configuresinteractive_features(self) -> None:

        session = create_prompt_session(output=DummyOutput())
        assert session.multiline is True
        assert isinstance(session.completer, CommandCompleter)
        assert {binding.keys for binding in session.key_bindings.bindings} == {
            (Keys.ControlM,),
            (Keys.Escape, Keys.ControlM),
        }
        with patch.object(session, "prompt", return_value="answer") as prompt:
            assert prompt("你> ") == "answer"
        prompt.assert_called_once_with("你> ")

    def testprompt_session_key_bindings_submit_and_insert_newline(self) -> None:

        session = create_prompt_session(output=DummyOutput())
        event = MagicMock()
        handlers = {binding.keys: binding.handler for binding in session.key_bindings.bindings}

        handlers[(Keys.ControlM,)](event)
        handlers[(Keys.Escape, Keys.ControlM)](event)

        event.current_buffer.validate_and_handle.assert_called_once_with()
        event.current_buffer.insert_text.assert_called_once_with("\n")

    def test_command_completer_completes_commands_only(self) -> None:

        completer = CommandCompleter()
        completions = list(completer.get_completions(Document("/q"), None))
        assert [completion.text for completion in completions] == ["/quit"]
        assert list(completer.get_completions(Document("hello"), None)) == []
        assert list(completer.get_completions(Document("/new arg"), None)) == []

    def test_command_completer_handles_missing_text_and_unknown_command(self) -> None:
        completer = CommandCompleter()

        assert list(completer.get_completions(SimpleNamespace(), None)) == []
        assert list(completer.get_completions(Document("/unknown"), None)) == []

    def test_command_completer_sets_replacement_position(self) -> None:
        completer = CommandCompleter()

        completions = list(completer.get_completions(Document("/qu"), None))

        assert len(completions) == 1
        assert completions[0].text == "/quit"
        assert completions[0].start_position == -3
