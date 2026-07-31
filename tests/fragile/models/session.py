from uuid import UUID

from fragile.models import SessionState


class TestSessionState:
    def test_session_state(self) -> None:
        state = SessionState(thread_id=UUID(int=1))

        assert state.thread_id == UUID(int=1)
        assert "prompt_session" not in SessionState.model_fields

    def test_session_state_is_mutable(self) -> None:
        state = SessionState(thread_id=UUID(int=1))
        thread_id = UUID(int=2)

        state.thread_id = thread_id

        assert state.thread_id == thread_id
