from argparse import ArgumentParser

import uvicorn

from app.services.migration_service import upgrade_database


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="启动博客（自动迁移）")
    parser.add_argument("--port", type=int, default=8000)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    upgrade_database()
    uvicorn.run("app.main:app", host="127.0.0.1", port=args.port, reload=True, log_level="debug")


if __name__ == "__main__":
    main()
