from unittest.mock import MagicMock, patch

import pytest

from app.services.database_bootstrap_service import (
    DatabaseBootstrapError,
    UnsupportedDatabaseBootstrapError,
    build_maintenance_database_url,
    ensure_database_exists,
)


def test_build_maintenance_database_url_replaces_target_database_name() -> None:
    url = "postgresql+psycopg://postgres:123456@localhost:5432/myblog"

    result = build_maintenance_database_url(url)

    assert result.endswith("@localhost:5432/postgres")
    assert result.startswith("postgresql+psycopg://postgres:")


def test_build_maintenance_database_url_preserves_real_password_for_engine_connection() -> None:
    url = "postgresql+psycopg://postgres:123456@localhost:5432/myblog"

    result = build_maintenance_database_url(url)

    assert "***" not in result
    assert "123456" in result


def test_build_maintenance_database_url_rejects_non_postgresql_url() -> None:
    with pytest.raises(UnsupportedDatabaseBootstrapError):
        build_maintenance_database_url("sqlite:///./test.db")


def test_ensure_database_exists_skips_create_when_database_already_exists() -> None:
    scalar_result = MagicMock(return_value=True)
    execute_result = MagicMock(scalar=scalar_result)
    connection = MagicMock()
    connection.execute.return_value = execute_result
    context_manager = MagicMock()
    context_manager.__enter__.return_value = connection
    engine = MagicMock()
    engine.begin.return_value = context_manager

    with patch("app.services.database_bootstrap_service.create_engine", return_value=engine):
        ensure_database_exists("postgresql+psycopg://postgres:123456@localhost:5432/myblog")

    connection.execute.assert_called_once()


def test_ensure_database_exists_creates_database_when_missing() -> None:
    scalar_result = MagicMock(return_value=False)
    execute_result = MagicMock(scalar=scalar_result)
    connection = MagicMock()
    connection.execute.side_effect = [execute_result, None]
    context_manager = MagicMock()
    context_manager.__enter__.return_value = connection
    engine = MagicMock()
    engine.begin.return_value = context_manager
    engine.dialect.identifier_preparer.quote.side_effect = lambda value: f'"{value}"'

    with patch("app.services.database_bootstrap_service.create_engine", return_value=engine):
        ensure_database_exists("postgresql+psycopg://postgres:123456@localhost:5432/myblog")

    assert connection.execute.call_count == 2
    engine.dialect.identifier_preparer.quote.assert_called_once_with("myblog")


def test_ensure_database_exists_wraps_create_failures() -> None:
    connection = MagicMock()
    connection.execute.side_effect = RuntimeError("permission denied")
    context_manager = MagicMock()
    context_manager.__enter__.return_value = connection
    engine = MagicMock()
    engine.begin.return_value = context_manager

    with (
        patch("app.services.database_bootstrap_service.create_engine", return_value=engine),
        pytest.raises(DatabaseBootstrapError),
    ):
        ensure_database_exists("postgresql+psycopg://postgres:123456@localhost:5432/myblog")
