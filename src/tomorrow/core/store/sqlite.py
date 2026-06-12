from langgraph.store.sqlite.aio import AsyncSqliteStore

from tomorrow.conf import settings
from tomorrow.models.constants import StoreType


def get_store() -> AsyncSqliteStore:
    store_config = settings.STORE.get(StoreType.SQLITE, {})
    path = store_config.get("path")
    if not path:
        raise ValueError("path is required for SQLite store")
    return AsyncSqliteStore.from_conn_string(path)
