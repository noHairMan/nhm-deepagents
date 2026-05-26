from langgraph.checkpoint.memory import InMemorySaver


def get_checkpoint_saver():
    return InMemorySaver()
