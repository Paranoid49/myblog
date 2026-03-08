import argparse

import uvicorn
from sqlalchemy.engine import make_url

from app.core.config import settings


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_APP = "app.main:app"
DEFAULT_LOG_LEVEL = "debug"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    return parser


def build_startup_summary(port: int) -> list[str]:
    return [
        f"APP={DEFAULT_APP}",
        f"HOST={DEFAULT_HOST}",
        f"PORT={port}",
        "RELOAD=True",
        f"LOG_LEVEL={DEFAULT_LOG_LEVEL}",
    ]


def build_masked_database_summary(database_url: str) -> list[str]:
    try:
        url = make_url(database_url)
    except Exception:
        return ["DATABASE_URL=<invalid>"]
    masked_url = str(url.set(password="***")) if url.password is not None else str(url)
    return [
        f"DATABASE_URL={masked_url}",
        f"DB_HOST={url.host}",
        f"DB_PORT={url.port}",
        f"DB_NAME={url.database}",
        f"DB_USER={url.username}",
    ]


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    for line in build_startup_summary(args.port):
        print(line)
    for line in build_masked_database_summary(settings.database_url):
        print(line)
    uvicorn.run(
        DEFAULT_APP,
        host=DEFAULT_HOST,
        port=args.port,
        reload=True,
        log_level=DEFAULT_LOG_LEVEL,
    )


if __name__ == "__main__":
    main()
