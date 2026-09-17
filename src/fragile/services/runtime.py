"""Runtime-scoped service dependencies."""

from contextvars import ContextVar
from dataclasses import dataclass

from fragile.services.account import AccountService
from fragile.services.conversation import ConversationService
from fragile.services.session import SessionService


@dataclass(frozen=True)
class RuntimeServices:
    """All persistence services sharing one initialized session factory."""

    account: AccountService
    conversation: ConversationService
    session: SessionService


current_services: ContextVar[RuntimeServices | None] = ContextVar("fragile_runtime_services", default=None)
