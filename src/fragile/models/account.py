"""Persistent credentials for the configured language model provider."""

from urllib.parse import urlparse

from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column

from fragile.exceptions import FragileError
from fragile.models.base import Base, get_initialized_session_factory
from tomorrow.conf import settings as tomorrow_settings
from tomorrow.models.constants import ModelType


class InvalidAccountError(FragileError, ValueError):
    """Raised when account credentials are incomplete or malformed."""


class Account(Base):
    """The single persisted account used by Fragile's model configuration."""

    __tablename__ = "fragile_account"

    singleton: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, default="default")
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    api_key: Mapped[str] = mapped_column(String, nullable=False)
    base_url: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str | None] = mapped_column(String(256), nullable=True)

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
                if account.provider != normalized_provider:
                    account.model = None
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

    @staticmethod
    def validate_model_selection(provider: str, model: str) -> tuple[str, str]:
        """Validate and normalize a selected provider model."""
        normalized_provider = provider.strip().lower()
        normalized_model = model.strip()
        try:
            ModelType(normalized_provider)
        except ValueError as exc:
            raise InvalidAccountError(f"unsupported model provider: {provider}") from exc
        if not normalized_model:
            raise InvalidAccountError("model must not be empty")
        return normalized_provider, normalized_model

    @classmethod
    async def save_model_selection(cls, provider: str, model: str) -> None:
        """Persist the selected model for the configured account provider."""
        normalized_provider, normalized_model = cls.validate_model_selection(provider, model)
        session_factory = await get_initialized_session_factory()
        async with session_factory() as session:
            account = await session.scalar(select(cls).where(cls.singleton == "default"))
            if account is None:
                raise InvalidAccountError("account must be configured before selecting a model")
            if account.provider != normalized_provider:
                raise InvalidAccountError("selected model provider does not match the configured account")
            account.model = normalized_model
            await session.commit()

    @classmethod
    async def get_model_selection(cls) -> tuple[str, str] | None:
        """Return the persisted provider and selected model, if present."""
        session_factory = await get_initialized_session_factory()
        async with session_factory() as session:
            account = await session.scalar(select(cls).where(cls.singleton == "default"))
            if account is None or account.model is None or not account.model.strip():
                return None
            return account.provider.strip().lower(), account.model.strip()


async def restore_account_configuration() -> bool:
    """Apply the persisted provider and credentials to Tomorrow's model configuration."""
    credentials = await Account.get_credentials()
    if credentials is None:
        return False
    provider, api_key, base_url = credentials
    normalized_provider = provider.strip().lower()
    try:
        model_type = ModelType(normalized_provider)
    except ValueError as exc:
        raise InvalidAccountError(f"unsupported model provider: {provider}") from exc

    model_configs = {
        ModelType.ANTHROPIC: tomorrow_settings.MODEL.anthropic,
        ModelType.OPENAI: tomorrow_settings.MODEL.openai,
    }
    tomorrow_settings.MODEL.type = model_type
    model_config = model_configs[model_type]
    model_config.base_url = base_url
    if model_type in {ModelType.ANTHROPIC, ModelType.OPENAI}:
        model_config.api_key = api_key
    selection = await Account.get_model_selection()
    if selection is not None:
        selected_provider, selected_model = selection
        if selected_provider == normalized_provider:
            model_config.model = selected_model
    return True
