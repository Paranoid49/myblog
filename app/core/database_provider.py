"""数据库引擎工厂。

根据 DATABASE_URL 的驱动类型创建对应的 SQLAlchemy 引擎，
封装不同数据库的连接参数差异。
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url


def create_app_engine(database_url: str) -> Engine:
    """根据数据库 URL 创建引擎，自动处理不同数据库的参数差异。"""
    url = make_url(database_url)
    driver = url.drivername

    if driver.startswith("sqlite"):
        return create_engine(
            database_url,
            future=True,
            connect_args={"check_same_thread": False},
        )
    elif driver.startswith("postgresql"):
        return create_engine(
            database_url,
            future=True,
            pool_pre_ping=True,
        )
    else:
        raise ValueError(f"unsupported_database_driver:{driver}")
