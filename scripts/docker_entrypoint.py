"""Docker 容器入口脚本 — 确保数据库就绪后启动应用。"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.engine import make_url

from app.core.config import settings
from app.services.database_bootstrap_service import ensure_database_exists
from app.services.database_state_service import database_exists


def main() -> None:
    url = make_url(settings.database_url)

    # PostgreSQL 场景：数据库不存在时自动创建
    if url.drivername.startswith("postgresql") and not database_exists():
        print("数据库不存在，正在创建...")
        ensure_database_exists(settings.database_url)
        print("数据库创建完成")

    # 执行数据库迁移
    subprocess.check_call([sys.executable, "-m", "alembic", "upgrade", "head"])

    # 启动应用
    import os
    os.execvp(
        sys.executable,
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", "0.0.0.0", "--port", "8000",
         "--proxy-headers", "--forwarded-allow-ips=*"],
    )


if __name__ == "__main__":
    main()
