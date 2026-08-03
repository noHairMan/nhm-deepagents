"""Persistent credentials for the configured language model provider."""

from urllib.parse import urlparse

from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column

from fragile.exceptions import FragileError
from fragile.models.base import Base, get_initialized_session_factory
from tomorrow.conf import settings as tomorrow_settings


class InvalidAccountError(FragileError, ValueError):
    """Raised when account credentials are incomplete or malformed."""


class Account(Base):
    """The single persisted account used by Fragile's model configuration."""

    __tablename__ = "fragile_account"

    singleton: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, default="default")
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    api_key: Mapped[str] = mapped_column(String, nullable=False)
    base_url: Mapped[str] = mapped_column(String, nullable=False)

    @staticmethod
    def validate_credentials(provider: str, api_key: str, base_url: str) -> tuple[str, str, str]:
        """Validate and normalize account values before persistence."""
        normalized_provider = provider.strip().lower()
        normalized_key = api_key.strip()
        normalized_url = base_url.strip()
        parsed_url = urlparse(normalized_url)
        if not normalized_provider:
            raise InvalidAccountError("provider must not be empty")
        if not normalized_key:
            raise InvalidAccountError("api_key must not be empty")
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise InvalidAccountError("base_url must be a valid HTTP or HTTPS URL")
        return normalized_provider, normalized_key, normalized_url

    @classmethod
    async def save_credentials(cls, provider: str, api_key: str, base_url: str) -> None:
        """Create or update the singleton account in one transaction."""
        normalized_provider, normalized_key, normalized_url = cls.validate_credentials(provider, api_key, base_url)
        session_factory = await get_initialized_session_factory()
        async with session_factory() as session:
            account = await session.scalar(select(cls).where(cls.singleton == "default"))
            if account is None:
                session.add(
                    cls(
                        singleton="default",
                        provider=normalized_provider,
                        api_key=normalized_key,
                        base_url=normalized_url,
                    )
                )
            else:
                account.provider = normalized_provider
                account.api_key = normalized_key
                account.base_url = normalized_url
            await session.commit()

    @classmethod
    async def get_credentials(cls) -> tuple[str, str, str] | None:
        """Return persisted credentials, or ``None`` when none are configured."""
        session_factory = await get_initialized_session_factory()
        async with session_factory() as session:
            account = await session.scalar(select(cls).where(cls.singleton == "default"))
            return None if account is None else (account.provider, account.api_key, account.base_url)


async def restore_account_configuration() -> bool:
    """Apply the persisted provider and credentials to Tomorrow's model configuration."""
    credentials = await Account.get_credentials()
    if credentials is None:
        return False
    provider, api_key, base_url = credentials
    tomorrow_settings.MODEL.type = provider
    model_config = tomorrow_settings.MODEL.anthropic
    model_config.api_key = api_key
    model_config.base_url = base_url
    return True
