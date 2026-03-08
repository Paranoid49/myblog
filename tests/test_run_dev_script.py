from unittest.mock import patch

import pytest

from scripts.run_dev import main


def test_run_dev_uses_default_uvicorn_settings() -> None:
    with patch("scripts.run_dev.uvicorn.run") as mock_run:
        main([])

    mock_run.assert_called_once_with(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="debug",
    )


def test_run_dev_allows_overriding_port() -> None:
    with patch("scripts.run_dev.uvicorn.run") as mock_run:
        main(["--port", "8001"])

    mock_run.assert_called_once_with(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="debug",
    )


def test_run_dev_rejects_non_integer_port() -> None:
    with pytest.raises(SystemExit):
        main(["--port", "not-a-number"])


def test_run_dev_prints_masked_database_summary(capsys) -> None:
    with (
        patch("app.core.config.settings.database_url", "postgresql+psycopg://postgres:123456@localhost:5432/myblog"),
        patch("scripts.run_dev.uvicorn.run"),
    ):
        main([])

    output = capsys.readouterr().out
    assert "DATABASE_URL=postgresql+psycopg://postgres:***@localhost:5432/myblog" in output
    assert "DB_HOST=localhost" in output
    assert "DB_PORT=5432" in output
    assert "DB_NAME=myblog" in output
    assert "DB_USER=postgres" in output
    assert "123456" not in output


def test_run_dev_prints_startup_parameters(capsys) -> None:
    with patch("scripts.run_dev.uvicorn.run"):
        main(["--port", "8001"])

    output = capsys.readouterr().out
    assert "APP=app.main:app" in output
    assert "HOST=127.0.0.1" in output
    assert "PORT=8001" in output
    assert "RELOAD=True" in output
    assert "LOG_LEVEL=debug" in output


def test_run_dev_prints_invalid_database_url_marker_when_url_cannot_be_parsed(capsys) -> None:
    with (
        patch("app.core.config.settings.database_url", "not a valid database url"),
        patch("scripts.run_dev.uvicorn.run"),
    ):
        main([])

    output = capsys.readouterr().out
    assert "DATABASE_URL=<invalid>" in output
