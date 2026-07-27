from uuid import UUID

from fragile.models import SessionState


class TestSessionState:
    def test_session_state(self) -> None:
        prompt_session = object()
        state = SessionState(thread_id=UUID(int=1), prompt_session=prompt_session)

        assert state.thread_id == UUID(int=1)
        assert state.prompt_session is prompt_session

    def test_session_state_is_mutable(self) -> None:
        state = SessionState(thread_id=UUID(int=1), prompt_session=object())
        thread_id = UUID(int=2)

        state.thread_id = thread_id

        assert state.thread_id == thread_id
