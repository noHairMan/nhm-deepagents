"""Account configuration application service."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from fragile.models.account import Account, InvalidAccountError
from fragile.repositories.account import AccountRepository
from tomorrow.conf import settings as tomorrow_settings
from tomorrow.models.constants import ModelType


class AccountService:
    """Coordinate account persistence and application configuration."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.repository = AccountRepository(session_factory)

    async def get_credentials(self) -> tuple[str, str, str] | None:
        account = await self.repository.get()
        return None if account is None else (account.provider, account.api_key, account.base_url)

    async def get_model_selection(self) -> tuple[str, str] | None:
        account = await self.repository.get()
        if account is None or not account.model or not account.model.strip():
            return None
        return account.provider.strip().lower(), account.model.strip()

    async def save_credentials(self, provider: str, api_key: str, base_url: str) -> None:
        values = Account.validate_credentials(provider, api_key, base_url)
        await self.repository.save_credentials(*values)

    async def save_model_selection(self, provider: str, model: str) -> None:
        values = Account.validate_model_selection(provider, model)
        try:
            await self.repository.save_model(*values)
        except ValueError as error:
            raise InvalidAccountError(str(error)) from error

    async def restore_configuration(self) -> bool:
        credentials = await self.repository.get()
        if credentials is None:
            return False
        provider, api_key, base_url = credentials.provider.strip().lower(), credentials.api_key, credentials.base_url
        try:
            model_type = ModelType(provider)
        except ValueError as error:
            raise InvalidAccountError(f"unsupported model provider: {credentials.provider}") from error
        model_configs = {
            ModelType.ANTHROPIC: tomorrow_settings.MODEL.anthropic,
            ModelType.OPENAI: tomorrow_settings.MODEL.openai,
        }
        tomorrow_settings.MODEL.type = model_type
        model_config = model_configs[model_type]
        model_config.base_url = base_url
        model_config.api_key = api_key
        if credentials.model and credentials.model.strip():
            model_config.model = credentials.model.strip()
        return True
