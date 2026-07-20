"""LangGraph CLI entry point for the Tomorrow agent."""

from tomorrow.core.agent import AgentManager

graph = AgentManager.create_agent()
