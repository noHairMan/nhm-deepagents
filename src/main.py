import asyncio
import os


def get_unicorn_server():
    import uvicorn

    from rainy.conf import settings

    config = uvicorn.Config(
        "rainy.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_config=settings.LOGGING,
    )
    server = uvicorn.Server(config)
    return server


async def main():
    os.environ.setdefault("TOMORROW_APP", "tomorrow")
    os.environ.setdefault("TOMORROW_SETTINGS_MODULE", "tomorrow.settings")
    os.environ.setdefault("RAINY_APP", "rainy")
    os.environ.setdefault("RAINY_SETTINGS_MODULE", "rainy.settings")

    server = get_unicorn_server()
    return await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
