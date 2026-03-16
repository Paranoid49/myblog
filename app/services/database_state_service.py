from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.core.config import settings


def database_exists() -> bool:
    """检查目标数据库是否存在。SQLite 始终返回 True，PostgreSQL 实际查询。"""
    url = make_url(settings.database_url)
    if not url.drivername.startswith("postgresql"):
        return True

    engine = create_engine(url.set(database="postgres").render_as_string(hide_password=False), future=True)
    try:
        with engine.connect() as connection:
            return bool(
                connection.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
                    {"database_name": url.database},
                ).scalar()
            )
    except Exception:
        return False
    finally:
        engine.dispose()
