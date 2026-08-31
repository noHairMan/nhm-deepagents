import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from fragile.models import Account, InvalidAccountError
from fragile.models.base import get_engine


class TestAccount:
    @pytest.mark.asyncio
    async def test_save_and_update_credentials(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "account.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)
        async_engine = get_engine()
        monkeypatch.setattr("fragile.models.base.engine", async_engine)

        await Account.save_credentials("OpenAI", " key-one ", " https://one.example/v1 ")
        assert await Account.get_credentials() == ("openai", "key-one", "https://one.example/v1")
        await Account.save_credentials("OpenAI", "key-one-updated", "https://one.example/v1")
        assert await Account.get_credentials() == ("openai", "key-one-updated", "https://one.example/v1")
        await Account.save_credentials("Anthropic", "key-two", "https://two.example/v1")
        await async_engine.dispose()

        engine = create_engine(f"sqlite:///{database_path}")
        with Session(engine) as session:
            accounts = session.scalars(select(Account)).all()
            assert len(accounts) == 1
            assert accounts[0].api_key == "key-two"
            assert accounts[0].base_url == "https://two.example/v1"
            assert accounts[0].provider == "anthropic"
            assert accounts[0].model is None
        engine.dispose()

    @pytest.mark.asyncio
    async def test_get_credentials_returns_none_without_account(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "empty-account.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)
        async_engine = get_engine()
        monkeypatch.setattr("fragile.models.base.engine", async_engine)
        assert await Account.get_credentials() is None
        await async_engine.dispose()

    @pytest.mark.asyncio
    async def test_save_and_get_model_selection(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "model-selection.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)
        async_engine = get_engine()
        monkeypatch.setattr("fragile.models.base.engine", async_engine)

        await Account.save_credentials("OpenAI", "key", "https://example.com/v1")
        await Account.save_model_selection(" OpenAI ", " gpt-5 ")

        assert await Account.get_model_selection() == ("openai", "gpt-5")
        await async_engine.dispose()

    @pytest.mark.asyncio
    async def test_saving_credentials_for_new_provider_clears_model_selection(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "changed-provider.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)
        async_engine = get_engine()
        monkeypatch.setattr("fragile.models.base.engine", async_engine)

        await Account.save_credentials("OpenAI", "key", "https://example.com/v1")
        await Account.save_model_selection("openai", "gpt-5")
        await Account.save_credentials("Anthropic", "new-key", "https://anthropic.example/v1")

        assert await Account.get_model_selection() is None
        await async_engine.dispose()

    @pytest.mark.asyncio
    async def test_save_model_selection_rejects_missing_or_mismatched_account(self, tmp_path, monkeypatch) -> None:
        database_path = tmp_path / "missing-account.db"
        monkeypatch.setattr("fragile.models.base.settings.CHECKPOINT.sqlite.path", database_path)
        async_engine = get_engine()
        monkeypatch.setattr("fragile.models.base.engine", async_engine)

        with pytest.raises(InvalidAccountError, match="account must be configured"):
            await Account.save_model_selection("openai", "gpt-5")
        await Account.save_credentials("OpenAI", "key", "https://example.com/v1")
        with pytest.raises(InvalidAccountError, match="does not match"):
            await Account.save_model_selection("anthropic", "claude-sonnet-5")
        await async_engine.dispose()

    @pytest.mark.parametrize(
        ("provider", "api_key", "base_url", "message"),
        [
            ("", "key", "https://example.com", "provider"),
            ("OpenAI", "", "https://example.com", "api_key"),
            ("OpenAI", "key", "not-a-url", "base_url"),
        ],
    )
    def test_validate_credentials_rejects_invalid_values(
        self, provider: str, api_key: str, base_url: str, message: str
    ) -> None:
        with pytest.raises(InvalidAccountError, match=message):
            Account.validate_credentials(provider, api_key, base_url)

    @pytest.mark.parametrize(
        ("provider", "model", "message"),
        [("vertex", "model", "unsupported"), ("openai", "  ", "model")],
    )
    def test_validate_model_selection_rejects_invalid_values(self, provider: str, model: str, message: str) -> None:
        with pytest.raises(InvalidAccountError, match=message):
            Account.validate_model_selection(provider, model)
