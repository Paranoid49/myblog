#!/usr/bin/env python
"""
清空数据库脚本 - 用于测试初始化功能

用法:
    python scripts/clear_database.py           # 清空当前数据库
    python scripts/clear_database.py --force   # 跳过确认直接清空
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.core.config import settings


def clear_sqlite_database(db_path: str) -> None:
    """删除 SQLite 数据库文件"""
    path = Path(db_path)
    if path.exists():
        path.unlink()
        print(f"已删除 SQLite 数据库文件: {path}")
    else:
        print(f"SQLite 数据库文件不存在: {path}")


def clear_postgresql_database(database_url: str) -> None:
    """删除 PostgreSQL 数据库"""
    url = make_url(database_url)
    db_name = url.database

    # 连接到 postgres 默认数据库
    postgres_url = url.set(database="postgres").render_as_string(hide_password=False)
    engine = create_engine(postgres_url, isolation_level="AUTOCOMMIT")

    try:
        with engine.connect() as conn:
            # 断开所有连接
            conn.execute(
                text(
                    f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{db_name}'
                AND pid <> pg_backend_pid()
                """
                )
            )
            # 删除数据库
            conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
            print(f"已删除 PostgreSQL 数据库: {db_name}")
    except Exception as e:
        print(f"删除 PostgreSQL 数据库失败: {e}")
        raise
    finally:
        engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="清空数据库")
    parser.add_argument("--force", action="store_true", help="跳过确认直接清空")
    args = parser.parse_args()

    database_url = settings.database_url
    url = make_url(database_url)

    print(f"数据库类型: {url.drivername}")
    print(f"数据库地址: {url.host}:{url.port}" if url.host else f"数据库文件: {url.database}")

    if not args.force:
        confirm = input("\n确定要清空数据库吗? [y/N]: ")
        if confirm.lower() != "y":
            print("已取消")
            return

    if url.drivername.startswith("sqlite"):
        db_path = url.database
        if db_path:
            clear_sqlite_database(db_path)
        else:
            print("SQLite 数据库路径无效")
    elif url.drivername.startswith("postgresql"):
        clear_postgresql_database(database_url)
    else:
        print(f"不支持的数据库类型: {url.drivername}")
        sys.exit(1)

    print("\n数据库已清空，可以重新运行初始化流程")


if __name__ == "__main__":
    main()