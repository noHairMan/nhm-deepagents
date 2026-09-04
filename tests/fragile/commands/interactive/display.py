from unittest.mock import patch
from uuid import UUID

from fragile.commands.interactive.display import (
    TimelineRenderer,
    enter_fullscreen,
    leave_fullscreen,
    print_stream,
    print_thinking,
    replay_outputs,
    show_connection_error,
    show_request_error,
    show_startup,
)
from fragile.commands.interactive.trace import TraceEvent, trace_to_json


class TestDisplay:
    def test_show_connection_error_redacts_credentials(self, capsys) -> None:
        show_connection_error("anthropic", "claude-test", "https://user:secret@example.test:443/api")

        output = capsys.readouterr().out
        assert "provider: anthropic" in output
        assert "claude-test" in output
        assert "https://example.test:443/api" in output
        assert "secret" not in output

    def test_show_connection_error_does_not_use_red_background(self) -> None:
        with patch("fragile.commands.interactive.display.console.print") as print_console:
            show_connection_error()

        error_text = print_console.call_args.args[0]
        assert error_text.style == "bold red"

    def test_show_request_error_uses_red_style(self) -> None:
        with patch("fragile.commands.interactive.display.console.print") as print_console:
            show_request_error("invalid request")

        error_text = print_console.call_args.args[0]
        assert error_text.style == "bold red"

    def test_print_stream(self, capsys) -> None:
        print_stream("answer")

        assert capsys.readouterr().out == "answer"

    def test_print_stream_preserves_rich_markup_as_plain_text(self, capsys) -> None:
        print_stream("[not-a-markup-tag]answer[/not-a-markup-tag]")

        assert capsys.readouterr().out == "[not-a-markup-tag]answer[/not-a-markup-tag]"

    def test_print_thinking_uses_safe_distinct_style(self) -> None:
        with patch("fragile.commands.interactive.display.console.print") as print_console:
            print_thinking("[thinking]")

        thinking_text = print_console.call_args.args[0]
        assert thinking_text.plain == "[thinking]"
        assert thinking_text.style == "dim yellow"

    def test_print_thinking_ignores_empty_content(self) -> None:
        with patch("fragile.commands.interactive.display.console.print") as print_console:
            print_thinking("")

        print_console.assert_not_called()

    def test_timeline_merges_adjacent_model_content(self, capsys) -> None:
        renderer = TimelineRenderer()

        renderer.render(TraceEvent(0, "thinking", content="first"))
        renderer.render(TraceEvent(1, "thinking", content=" second"))
        renderer.render(TraceEvent(2, "text", content="[bold]answer"))
        renderer.render(TraceEvent(3, "text", content="[/bold]"))
        renderer.finish()

        output = capsys.readouterr().out
        assert output.count("Thinking (provider summary)") == 1
        assert output.count("Assistant") == 1
        assert "[bold]answer[/bold]" in output

    def test_timeline_renders_tool_command_result_and_failure(self, capsys) -> None:
        renderer = TimelineRenderer()
        renderer.render(
            TraceEvent(
                0,
                "tool_start",
                name="execute",
                content="echo [bold]safe[/bold]",
                input={"command": "echo [bold]safe[/bold]"},
                status="running",
            )
        )
        renderer.render(TraceEvent(1, "tool_end", name="execute", output="done", status="completed"))
        renderer.render(TraceEvent(2, "tool_error", name="read_file", content="missing", status="failed"))

        output = capsys.readouterr().out
        assert "⠋ Tool: execute" in output
        assert "Command:" in output
        assert "Completed: execute" in output
        assert "Result:" in output
        assert "Failed: read_file" in output
        assert "[bold]safe[/bold]" in output

    def test_timeline_marks_long_blocks_as_truncated(self, capsys) -> None:
        renderer = TimelineRenderer()
        renderer.render(TraceEvent(0, "tool_end", name="read_file", output="x" * 5000, status="completed"))

        assert "… [truncated]" in capsys.readouterr().out

    def test_timeline_renders_real_subagent_stage_input(self, capsys) -> None:
        renderer = TimelineRenderer()
        renderer.render(
            TraceEvent(0, "stage", name="research_subagent", content="phase", input={"task": "work"}, status="running")
        )

        output = capsys.readouterr().out
        assert "⠋ Subagent: research_subagent" in output
        assert "phase" in output
        assert '"task": "work"' in output

    def test_timeline_omits_generic_stage_without_tool_or_skill_call(self, capsys) -> None:
        TimelineRenderer().render(TraceEvent(0, "stage", name="agent", status="running"))

        assert capsys.readouterr().out == ""

    def test_timeline_renders_skill_status_without_details(self, capsys) -> None:
        TimelineRenderer().render(TraceEvent(0, "stage", name="format_skill", status="completed"))

        output = capsys.readouterr().out
        assert "✓ Skill: format_skill" in output

    def test_timeline_ignores_unknown_event_kind(self, capsys) -> None:
        TimelineRenderer().render(TraceEvent(0, "unknown"))

        assert capsys.readouterr().out == ""

    def test_replay_outputs_preserves_markup(self, capsys) -> None:
        record = type("Record", (), {"user_input": "question", "assistant_output": "[bold]answer[/bold]"})()

        replay_outputs([record])

        output = capsys.readouterr().out
        assert "> question" in output
        assert "answer" in output

    def test_replay_outputs_skips_registered_system_commands(self, capsys) -> None:
        records = [
            type("Record", (), {"user_input": "/model", "assistant_output": "hidden"})(),
            type("Record", (), {"user_input": "question", "assistant_output": "answer"})(),
        ]

        replay_outputs(records)

        output = capsys.readouterr().out
        assert "> /model" not in output
        assert "hidden" not in output
        assert "> question" in output
        assert "answer" in output

    def test_replay_outputs_shows_thinking_before_answer_safely(self, capsys) -> None:
        record = type(
            "Record",
            (),
            {
                "user_input": "question",
                "thinking_output": "[thinking]reasoning[/thinking]",
                "assistant_output": "answer",
            },
        )()

        replay_outputs([record])

        output = capsys.readouterr().out
        assert output.index("Thinking (provider summary)") < output.index("reasoning") < output.index("answer")
        assert "[thinking]reasoning[/thinking]" in output

    def test_replay_outputs_uses_persisted_trace(self, capsys) -> None:
        trace_payload = trace_to_json(
            [
                TraceEvent(2, "text", content="answer"),
                TraceEvent(1, "tool_end", name="read_file", output="result", status="completed"),
            ]
        )
        record = type("Record", (), {"user_input": "question", "trace_payload": trace_payload})()

        replay_outputs([record])

        output = capsys.readouterr().out
        assert output.index("Completed: read_file") < output.index("answer")

    def test_replay_outputs_supports_legacy_record_without_thinking(self, capsys) -> None:
        record = type("Record", (), {"user_input": "question", "assistant_output": "answer"})()

        replay_outputs([record])

        output = capsys.readouterr().out
        assert "Thinking:" not in output
        assert "answer" in output

    def test_replay_outputs_handles_empty_assistant_content(self, capsys) -> None:
        record = type("Record", (), {"user_input": "question", "assistant_output": ""})()

        replay_outputs([record])

        assert "> question" in capsys.readouterr().out

    def test_fullscreen_uses_isolated_terminal_screen(self, capsys) -> None:

        enter_fullscreen()
        leave_fullscreen()

        assert capsys.readouterr().out == "\033[?1049h\033[?1049l"

    def test_startup_display_for_new_session(self, capsys) -> None:

        show_startup(UUID(int=1), False)

        output = capsys.readouterr().out
        assert "Fresh start" in output
        assert "All previous messages and task state have been cleared" in output
        assert "Tomorrow agent client is ready" in output
        assert "Fragile is ready" in output

    def test_startup_display_for_resumed_session(self, capsys) -> None:

        show_startup(UUID(int=1), True)

        output = capsys.readouterr().out
        assert "Resumed conversation" in output
        assert "Fresh start" not in output
