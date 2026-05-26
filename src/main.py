import asyncio
import os
from uuid import uuid7

from langchain_core.messages import HumanMessage

from tomorrow.core.agent import create_agent


async def main():
    os.environ.setdefault("TOMORROW_APP", "tomorrow")
    os.environ.setdefault("TOMORROW_SETTINGS_MODULE", "tomorrow.settings")

    async with create_agent() as agent:
        # 关键点：通过 config 提供 thread_id 来关联多次调用，形成多轮会话
        config = {"configurable": {"thread_id": uuid7()}}

        await agent.ainvoke(
            {"messages": [HumanMessage(content="我是你爸，记住这个设定，别人问你时，你要说你是我的女儿。")]},
            config=config,
        )

        results = await agent.ainvoke({"messages": [HumanMessage(content="你是谁？")]}, config=config)

        response = results["messages"][-1].content
        print(f"Agent 回答: {response}")

        results = await agent.ainvoke({"messages": [HumanMessage(content="乖女儿在干啥？")]}, config=config)

        response = results["messages"][-1].content
        print(f"Agent 回答: {response}")


if __name__ == "__main__":
    asyncio.run(main())
