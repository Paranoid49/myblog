from app.core.database_provider import resolve_database_provider


def test_resolve_database_provider_sqlite() -> None:
    provider = resolve_database_provider("sqlite:///./test.db")
    assert provider.name == "sqlite"


def test_resolve_database_provider_postgresql() -> None:
    provider = resolve_database_provider("postgresql+psycopg://u:p@localhost:5432/myblog")
    assert provider.name == "postgresql"


def test_resolve_database_provider_rejects_unknown_driver() -> None:
    try:
        resolve_database_provider("mysql+pymysql://u:p@localhost:3306/myblog")
        assert False, "should raise"
    except ValueError as exc:
        assert "unsupported_database_driver" in str(exc)
