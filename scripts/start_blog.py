from argparse import ArgumentParser

import uvicorn
from sqlalchemy.engine import make_url

from app.core.config import settings
from app.services.database_bootstrap_service import ensure_database_exists
from app.services.database_state_service import database_exists
from app.services.migration_service import upgrade_database


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="启动博客（自动迁移）")
    parser.add_argument("--port", type=int, default=8000)
    return parser


def _should_bootstrap_database() -> bool:
    return make_url(settings.database_url).drivername.startswith("postgresql")


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    # 确保数据库存在
    if _should_bootstrap_database() and not database_exists():
        print("数据库不存在，正在创建...")
        ensure_database_exists(settings.database_url)
        print("数据库创建完成")

    upgrade_database()
    uvicorn.run("app.main:app", host="127.0.0.1", port=args.port, reload=True, log_level="debug")


if __name__ == "__main__":
    main()
