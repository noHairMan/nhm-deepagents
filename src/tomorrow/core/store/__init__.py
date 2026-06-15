from typing import Optional

from langgraph.store.base import BaseStore

from tomorrow.conf import settings
from tomorrow.models.constants import StoreType


def get_store() -> Optional[BaseStore]:
    if not hasattr(settings, "STORE"):
        return None
    store_type = settings.STORE.get("type")
    match store_type:
        case StoreType.SQLITE:
            from .sqlite import get_store as get_sqlite_store

            return get_sqlite_store()
        case StoreType.MEMORY:
            from .memory import get_store as get_memory_store

            return get_memory_store()
        case _:
            raise ValueError(f"Unsupported store type: {store_type}")
