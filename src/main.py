import os
from pathlib import Path


def run_server():
    import uvicorn

    from rainy.conf import settings

    uvicorn.run(
        "rainy.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        reload_dirs=[
            str(Path(__file__).resolve().parent / "rainy"),
            str(Path(__file__).resolve().parent / "tomorrow"),
        ],
        log_config=settings.LOGGING.to_dict(),
    )


def main():
    os.environ.setdefault("TOMORROW_APP", "tomorrow")
    os.environ.setdefault("TOMORROW_SETTINGS_MODULE", "tomorrow.settings")
    os.environ.setdefault("RAINY_APP", "rainy")
    os.environ.setdefault("RAINY_SETTINGS_MODULE", "rainy.settings")

    run_server()


if __name__ == "__main__":
    main()
