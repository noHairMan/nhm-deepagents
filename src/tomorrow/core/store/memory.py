from langgraph.store.memory import InMemoryStore


def get_store() -> InMemoryStore:
    return InMemoryStore()
