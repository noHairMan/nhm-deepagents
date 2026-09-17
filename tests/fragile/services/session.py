import uuid

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from fragile.services.session import SessionService


class TestSessionService:
    @pytest.mark.asyncio
    async def test_save_and_list(self, session_factory: async_sessionmaker) -> None:
        service = SessionService(session_factory)
        thread_id = uuid.uuid4()

        await service.save(thread_id, "user input", "assistant output", "style", "thinking", "trace")

        outputs = await service.list_for_thread(thread_id)
        assert len(outputs) == 1
        assert outputs[0].user_input == "user input"
        assert outputs[0].assistant_output == "assistant output"
