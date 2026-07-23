from unittest.mock import MagicMock, patch

from prompt_toolkit.document import Document
from prompt_toolkit.keys import Keys

from fragile.commands.interactive.input import CommandCompleter, create_prompt_session, prompt


class TestInput:
    def test_prompt(self) -> None:
        session = MagicMock()
        session.prompt.return_value = "answer"

        assert prompt(session) == "answer"
        session.prompt.assert_called_once_with("你> ")

    def testprompt_session_configuresinteractive_features(self) -> None:

        session = create_prompt_session()
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

        session = create_prompt_session()
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
