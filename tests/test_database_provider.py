from sqlalchemy.pool import NullPool

from app.core.database_provider import (
    PostgreSQLDatabaseProvider,
    SQLiteDatabaseProvider,
    resolve_database_provider,
)


def test_resolve_database_provider_sqlite() -> None:
    provider = resolve_database_provider("sqlite:///./test.db")
    assert provider.name == "sqlite"
    assert isinstance(provider, SQLiteDatabaseProvider)


def test_resolve_database_provider_postgresql() -> None:
    provider = resolve_database_provider("postgresql+psycopg://u:p@localhost:5432/myblog")
    assert provider.name == "postgresql"
    assert isinstance(provider, PostgreSQLDatabaseProvider)


def test_sqlite_provider_creates_engine() -> None:
    provider = SQLiteDatabaseProvider()
    engine = provider.create_engine("sqlite:///:memory:")
    assert engine.dialect.name == "sqlite"
    engine.dispose()


def test_postgresql_provider_creates_engine() -> None:
    provider = PostgreSQLDatabaseProvider()
    engine = provider.create_engine("postgresql+psycopg://u:p@localhost:5432/myblog")
    assert engine.dialect.name == "postgresql"
    assert engine.pool.__class__ is not NullPool
    engine.dispose()


def test_resolve_database_provider_rejects_unknown_driver() -> None:
    try:
        resolve_database_provider("mysql+pymysql://u:p@localhost:3306/myblog")
        assert False, "should raise"
    except ValueError as exc:
        assert "unsupported_database_driver" in str(exc)
