from langgraph.store.base import BaseStore

from tomorrow.conf import settings
from tomorrow.exceptions import TomorrowStoreError
from tomorrow.models.constants import StoreType


def get_store() -> BaseStore:
    store_type = settings.STORE.get("type")
    match store_type:
        case StoreType.SQLITE:
            from .sqlite import get_store as get_sqlite_store

            return get_sqlite_store()
        case StoreType.MEMORY:
            from .memory import get_store as get_memory_store

            return get_memory_store()
        case _:
            raise TomorrowStoreError(f"Unsupported store type: {store_type}")
