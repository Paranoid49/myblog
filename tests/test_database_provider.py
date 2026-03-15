import pytest
from sqlalchemy.pool import NullPool

from app.core.database_provider import create_app_engine


def test_create_app_engine_sqlite() -> None:
    """验证 SQLite 驱动能正确创建引擎。"""
    engine = create_app_engine("sqlite:///:memory:")
    assert engine.dialect.name == "sqlite"
    engine.dispose()


def test_create_app_engine_postgresql() -> None:
    """验证 PostgreSQL 驱动能正确创建引擎。"""
    engine = create_app_engine("postgresql+psycopg://u:p@localhost:5432/myblog")
    assert engine.dialect.name == "postgresql"
    assert engine.pool.__class__ is not NullPool
    engine.dispose()


def test_create_app_engine_rejects_unknown_driver() -> None:
    """验证不支持的驱动类型抛出 ValueError。"""
    with pytest.raises(ValueError, match="unsupported_database_driver"):
        create_app_engine("mysql+pymysql://u:p@localhost:3306/myblog")
