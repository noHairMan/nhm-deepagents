import os
from pathlib import Path


def run_server(reload: bool = False):
    import uvicorn

    from rainy.conf import settings

    uvicorn.run(
        "rainy.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=reload,
        reload_dirs=[
            str(Path(__file__).resolve().parent / "rainy"),
            str(Path(__file__).resolve().parent / "tomorrow"),
        ],
        log_config=settings.LOGGING,
    )


def main():
    os.environ.setdefault("TOMORROW_APP", "tomorrow")
    os.environ.setdefault("TOMORROW_SETTINGS_MODULE", "tomorrow.settings")
    os.environ.setdefault("TOMORROW_ENV_FILE", ".env")
    os.environ.setdefault("RAINY_APP", "rainy")
    os.environ.setdefault("RAINY_SETTINGS_MODULE", "rainy.settings")
    os.environ.setdefault("RAINY_ENV_FILE", ".env")

    run_server()


if __name__ == "__main__":
    main()
