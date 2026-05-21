import asyncio
import os


async def main():
    os.environ.setdefault("TOMORROW_APP", "tomorrow")
    os.environ.setdefault("TOMORROW_SETTINGS_MODULE", "tomorrow.settings")

    from tomorrow.core.agent import agent

    result = await agent.ainvoke({"messages": [{"role": "user", "content": "你是谁?"}]})
    print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
