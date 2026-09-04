"""Interactive session orchestration."""

import logging
import time

import asyncclick as click
import httpx
from langchain_anthropic.chat_models import AnthropicInvalidRequestError
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph

from fragile.commands.interactive.agent import agent_runtime, chat, create_agent
from fragile.commands.interactive.commands import command_registry
from fragile.commands.interactive.display import (
    enter_fullscreen,
    leave_fullscreen,
    show_connection_error,
    show_request_error,
    show_startup,
)
from fragile.commands.interactive.input import (
    clear_submitted_input,
    clear_submitted_input_after_interaction,
    create_prompt_session,
)
from fragile.conf import settings
from fragile.exceptions import AgentResponseError
from fragile.models import ConversationHistory, SessionState, restore_account_configuration
from fragile.models.constants import CommandResult
from fragile.utils.uid import resolve_thread_id
from tomorrow.conf import settings as tomorrow_settings

logger = logging.getLogger(__name__)


class InteractiveSession:
    """Coordinate the lifecycle and state of an interactive session."""

    def __init__(self, thread: str | None) -> None:
        self.thread = thread
        self.thread_id = resolve_thread_id(thread)
        self.session = create_prompt_session()
        self.state = SessionState(thread_id=self.thread_id)
        self.is_running = True
        self.last_keyboard_interrupt: float | None = None

    async def run(self) -> None:
        """Run the interactive session until an exit action is received."""
        enter_fullscreen()
        try:
            show_startup(self.thread_id, self.thread is not None)
            async with agent_runtime() as (agent, checkpointer):
                while self.is_running:
                    agent = await self.run_iteration(agent, checkpointer)
        finally:
            leave_fullscreen()

    async def run_iteration(
        self, agent: CompiledStateGraph, checkpointer: BaseCheckpointSaver | None
    ) -> CompiledStateGraph:
        """Read and process one prompt when the session is running."""
        user_input = await self.read_input()
        if user_input is None:
            return agent
        is_registered_command = command_registry.is_registered(user_input)
        if is_registered_command:
            clear_submitted_input(self.session.output, user_input)
        try:
            result = await command_registry.handle(user_input, self.state)
            return await self.handle_result(agent, checkpointer, result, user_input)
        finally:
            if is_registered_command:
                if command_registry.clears_output_after_handling(user_input):
                    clear_submitted_input_after_interaction(self.session.output, user_input)
                else:
                    clear_submitted_input(self.session.output, user_input)

    async def read_input(self) -> str | None:
        """Read one prompt, handling retryable and terminating interrupts."""
        try:
            user_input = await self.session.prompt_async("> ")
        except KeyboardInterrupt, EOFError, click.Abort:
            click.echo()
            now = time.monotonic()
            if (
                self.last_keyboard_interrupt is not None
                and now - self.last_keyboard_interrupt <= settings.INTERRUPT_EXIT_THRESHOLD
            ):
                self.is_running = False
            else:
                self.last_keyboard_interrupt = now
            return None
        self.last_keyboard_interrupt = None
        return user_input.strip()

    async def handle_result(
        self,
        agent: CompiledStateGraph,
        checkpointer: BaseCheckpointSaver | None,
        result: CommandResult,
        user_input: str,
    ) -> CompiledStateGraph:
        """Apply a command result or process an ordinary chat prompt."""
        if result is CommandResult.EXIT:
            self.is_running = False
        elif result is CommandResult.MODEL_CHANGED:
            await restore_account_configuration()
            return create_agent(checkpointer)
        elif result is CommandResult.NOT_HANDLED and user_input:
            await ConversationHistory.register_conversation(self.state.thread_id, user_input)
            try:
                await chat(agent, user_input, self.state.thread_id)
            except httpx.ConnectError:
                model_type = str(tomorrow_settings.MODEL.get("type") or "unknown")
                model_config = tomorrow_settings.MODEL.get(model_type) or {}
                provider = model_type
                model = str(model_config.get("model", "unknown"))
                base_url = str(model_config.get("base_url") or "未配置")
                logger.exception(
                    "模型服务连接失败 provider=%s model=%s base_url=%s",
                    provider,
                    model,
                    base_url,
                )
                show_connection_error(provider, model, base_url)
            except (AnthropicInvalidRequestError, AgentResponseError) as error:
                model_type = str(tomorrow_settings.MODEL.get("type") or "unknown")
                model_config = tomorrow_settings.MODEL.get(model_type) or {}
                provider = model_type
                model = str(model_config.get("model", "unknown"))
                base_url = str(model_config.get("base_url") or "未配置")
                logger.exception(
                    "模型请求失败 provider=%s model=%s base_url=%s error=%s",
                    provider,
                    model,
                    base_url,
                    error,
                )
                show_request_error(str(error))
        return agent


async def interactive(
    thread: str | None,
) -> None:
    """Start an interactive session. Enter /quit to exit."""
    await InteractiveSession(thread).run()
