from datetime import date
from types import SimpleNamespace

from fragile.commands.interactive.trace import (
    StreamSegment,
    TraceEvent,
    content_segments,
    normalize_event,
    safe_value,
    trace_from_json,
    trace_to_json,
)


class TestTrace:
    def test_content_segments_and_text_support_provider_blocks(self) -> None:
        content = [
            "plain",
            {"type": "reasoning", "reasoning": "think"},
            {"thinking": "consider"},
            {"type": "text", "text": "answer"},
            {"type": "image", "data": "ignored"},
        ]

        assert content_segments(content) == [
            StreamSegment("text", "plain"),
            StreamSegment("thinking", "think"),
            StreamSegment("thinking", "consider"),
            StreamSegment("text", "answer"),
        ]

    def test_safe_value_redacts_sensitive_keys_and_url_credentials(self) -> None:
        value = safe_value(
            {
                "api_key": "secret",
                "nested": {"authorization": "Bearer secret"},
                "url": "https://user:password@example.test:443/api?x=1",
                "message": "api_key=inline-secret",
                "items": (1, {"password": "another"}),
            }
        )

        assert value == {
            "api_key": "[REDACTED]",
            "nested": {"authorization": "[REDACTED]"},
            "url": "https://example.test:443/api?x=1",
            "message": "api_key=[REDACTED]",
            "items": [1, {"password": "[REDACTED]"}],
        }

    def test_safe_value_handles_dates_and_unknown_objects(self) -> None:
        assert safe_value(date(2026, 9, 3)) == "2026-09-03"
        assert safe_value({1, 2}) == [1, 2]
        assert safe_value(SimpleNamespace(value=1)) == "<SimpleNamespace>"
        assert safe_value(b"bytes") == "<bytes>"

    def test_safe_value_handles_invalid_and_ipv6_credential_urls(self) -> None:
        assert safe_value("https://user:pass@[2001:db8::1]:443/path") == "https://[2001:db8::1]:443/path"
        assert safe_value("https://user:pass@example.test:notaport/path") == "https://example.test/path"
        assert safe_value("https://[invalid") == "https://[invalid"

    def test_normalize_model_event_assigns_sequences_and_run_metadata(self) -> None:
        event = {
            "event": "on_chat_model_stream",
            "run_id": "model-run",
            "parent_ids": ["agent-run"],
            "tags": ["stream"],
            "data": {
                "chunk": SimpleNamespace(
                    content=[{"type": "thinking", "thinking": "先想"}, {"type": "text", "text": "答案"}]
                )
            },
        }

        assert list(normalize_event(event, 4)) == [
            TraceEvent(
                4,
                "thinking",
                content="先想",
                run_id="model-run",
                parent_run_id="agent-run",
                metadata={"tags": ["stream"], "parent_ids": ["agent-run"]},
            ),
            TraceEvent(
                5,
                "text",
                content="答案",
                run_id="model-run",
                parent_run_id="agent-run",
                metadata={"tags": ["stream"], "parent_ids": ["agent-run"]},
            ),
        ]

    def test_normalize_tool_events_extracts_command_and_safe_values(self) -> None:
        start = {
            "event": "on_tool_start",
            "name": "execute",
            "run_id": "tool-run",
            "data": {"input": {"command": "echo [bold]safe[/bold]", "api_key": "secret"}},
        }
        end = {"event": "on_tool_end", "name": "execute", "data": {"output": "done"}}
        error = {"event": "on_tool_error", "name": "read_file", "data": {"error": "missing"}}

        assert list(normalize_event(start, 0))[0] == TraceEvent(
            0,
            "tool_start",
            name="execute",
            content="echo [bold]safe[/bold]",
            input={"command": "echo [bold]safe[/bold]", "api_key": "[REDACTED]"},
            status="running",
            run_id="tool-run",
        )
        assert list(normalize_event(end, 1))[0].output == "done"
        assert list(normalize_event(error, 2))[0].status == "failed"
        assert list(normalize_event(error, 2))[0].content == "missing"

    def test_normalize_tool_error_redacts_inline_credentials(self) -> None:
        event = {"event": "on_tool_error", "name": "execute", "data": {"error": "api_key=secret"}}

        assert list(normalize_event(event, 0))[0].content == "api_key=[REDACTED]"

    def test_normalize_tool_error_handles_non_string_errors_and_missing_command(self) -> None:
        error_event = {"event": "on_tool_error", "name": "execute", "data": {"error": ValueError("failed")}}
        no_command = {"event": "on_tool_start", "name": "execute", "data": {"input": {"command": 1}}}

        assert list(normalize_event(error_event, 0))[0].content == "<ValueError>"
        assert list(normalize_event(no_command, 1))[0].content is None

    def test_normalize_stage_events_keeps_agent_phases_and_ignores_noise(self) -> None:
        stage = {"event": "on_chain_start", "name": "subagent_research", "data": {"input": {"task": "find"}}}
        noise = {"event": "on_chain_start", "name": "RunnableSequence", "data": {"input": {}}}

        assert list(normalize_event(stage, 2))[0].kind == "stage"
        assert list(normalize_event(stage, 2))[0].status == "running"
        assert list(normalize_event(noise, 3)) == []

    def test_normalize_event_ignores_malformed_events(self) -> None:
        assert list(normalize_event(None, 0)) == []
        assert list(normalize_event({}, 0)) == []
        assert list(normalize_event({"event": "on_tool_start", "data": None}, 0)) == []
        assert list(normalize_event({"event": "unknown", "data": {}}, 0)) == []

    def test_normalize_event_handles_missing_model_chunk_and_tuple_parent_ids(self) -> None:
        model_event = {"event": "on_chat_model_stream", "run_id": 1, "parent_ids": (2,), "data": {"chunk": object()}}

        assert list(normalize_event(model_event, 0)) == []

    def test_normalize_stage_end_and_error_events(self) -> None:
        end = {"event": "on_chain_end", "name": "model", "data": {"output": {"answer": "ok"}}}
        error = {"event": "on_chain_error", "name": "agent", "data": {"error": ValueError("failed")}}
        no_name = {"event": "on_chain_start", "data": {"input": {}}}

        assert list(normalize_event(end, 0))[0].status == "completed"
        assert list(normalize_event(error, 1))[0].content == "<ValueError>"
        assert list(normalize_event(no_name, 2)) == []
        assert list(normalize_event({"event": "on_chain_start", "name": "worker", "data": {}}, 3)) == []

    def test_trace_json_round_trip_orders_events_and_handles_bad_data(self) -> None:
        events = [TraceEvent(2, "text", content="second"), TraceEvent(1, "tool_end", name="tool", status="completed")]

        payload = trace_to_json(events)

        assert [event.sequence for event in trace_from_json(payload)] == [1, 2]
        assert trace_from_json("not json") == []
        assert trace_from_json('{"not": "a list"}') == []
        assert trace_from_json('[{"sequence": "bad", "kind": "text"}]') == []
        assert trace_from_json('[{"sequence": 1, "kind": "unknown"}]') == []
