"""Persistence operations for the configured account."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from fragile.models.account import Account


class AccountRepository:
    """Persist and retrieve the singleton account using an injected factory."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def get(self) -> Account | None:
        """Return the configured account, if any."""
        async with self.session_factory() as session:
            return await session.scalar(select(Account).where(Account.singleton == "default"))

    async def save_credentials(self, provider: str, api_key: str, base_url: str) -> None:
        """Create or update account credentials."""
        async with self.session_factory() as session:
            account = await session.scalar(select(Account).where(Account.singleton == "default"))
            if account is None:
                session.add(Account(singleton="default", provider=provider, api_key=api_key, base_url=base_url))
            else:
                if account.provider != provider:
                    account.model = None
                account.provider = provider
                account.api_key = api_key
                account.base_url = base_url
            await session.commit()

    async def save_model(self, provider: str, model: str) -> None:
        """Persist a selected model for the configured provider."""
        async with self.session_factory() as session:
            account = await session.scalar(select(Account).where(Account.singleton == "default"))
            if account is None:
                raise ValueError("account must be configured before selecting a model")
            if account.provider != provider:
                raise ValueError("selected model provider does not match the configured account")
            account.model = model
            await session.commit()
