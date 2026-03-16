from unittest.mock import MagicMock, patch

from app.services.database_state_service import database_exists


def test_database_exists_returns_true_for_non_postgresql_url() -> None:
    with patch("app.services.database_state_service.settings.database_url", "sqlite:///./test.db"):
        assert database_exists() is True


def test_database_exists_returns_true_when_target_database_exists() -> None:
    connection = MagicMock()
    execute_result = MagicMock()
    execute_result.scalar.return_value = 1
    connection.execute.return_value = execute_result
    context_manager = MagicMock()
    context_manager.__enter__.return_value = connection

    engine = MagicMock()
    engine.connect.return_value = context_manager

    with (
        patch(
            "app.services.database_state_service.settings.database_url",
            "postgresql+psycopg://u:p@localhost:5432/myblog",
        ),
        patch("app.services.database_state_service.create_engine", return_value=engine),
    ):
        assert database_exists() is True


def test_database_exists_returns_false_when_target_database_missing() -> None:
    connection = MagicMock()
    execute_result = MagicMock()
    execute_result.scalar.return_value = 0
    connection.execute.return_value = execute_result
    context_manager = MagicMock()
    context_manager.__enter__.return_value = connection

    engine = MagicMock()
    engine.connect.return_value = context_manager

    with (
        patch(
            "app.services.database_state_service.settings.database_url",
            "postgresql+psycopg://u:p@localhost:5432/myblog",
        ),
        patch("app.services.database_state_service.create_engine", return_value=engine),
    ):
        assert database_exists() is False


def test_database_exists_returns_false_when_connection_raises() -> None:
    engine = MagicMock()
    engine.connect.side_effect = RuntimeError("boom")

    with (
        patch(
            "app.services.database_state_service.settings.database_url",
            "postgresql+psycopg://u:p@localhost:5432/myblog",
        ),
        patch("app.services.database_state_service.create_engine", return_value=engine),
    ):
        assert database_exists() is False


def test_database_exists_uses_unmasked_password_for_engine_url() -> None:
    connection = MagicMock()
    execute_result = MagicMock()
    execute_result.scalar.return_value = 1
    connection.execute.return_value = execute_result
    context_manager = MagicMock()
    context_manager.__enter__.return_value = connection

    engine = MagicMock()
    engine.connect.return_value = context_manager

    with (
        patch(
            "app.services.database_state_service.settings.database_url",
            "postgresql+psycopg://postgres:123456@localhost:5432/myblog",
        ),
        patch("app.services.database_state_service.create_engine", return_value=engine) as mock_create_engine,
    ):
        assert database_exists() is True

    called_url = mock_create_engine.call_args.args[0]
    assert "***" not in called_url
    assert "123456" in called_url
