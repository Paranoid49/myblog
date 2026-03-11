from unittest.mock import patch

from scripts.start_blog import main


def test_start_blog_runs_migration_and_uvicorn() -> None:
    with (
        patch("scripts.start_blog.ensure_database_exists") as mock_ensure_db,
        patch("scripts.start_blog.upgrade_database") as mock_upgrade,
        patch("scripts.start_blog.uvicorn.run") as mock_run,
    ):
        main([])

    mock_ensure_db.assert_not_called()
    mock_upgrade.assert_called_once()
    mock_run.assert_called_once_with(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="debug",
    )


def test_start_blog_allows_custom_port() -> None:
    with (
        patch("scripts.start_blog.ensure_database_exists"),
        patch("scripts.start_blog.upgrade_database"),
        patch("scripts.start_blog.uvicorn.run") as mock_run,
    ):
        main(["--port", "8010"])

    mock_run.assert_called_once_with(
        "app.main:app",
        host="127.0.0.1",
        port=8010,
        reload=True,
        log_level="debug",
    )


def test_start_blog_bootstraps_database_for_explicit_postgresql_url() -> None:
    with (
        patch("scripts.start_blog.settings.database_url", "postgresql+psycopg://postgres:postgres@localhost:5432/myblog"),
        patch("scripts.start_blog.database_exists", return_value=False),
        patch("scripts.start_blog.ensure_database_exists") as mock_ensure_db,
        patch("scripts.start_blog.upgrade_database") as mock_upgrade,
        patch("scripts.start_blog.uvicorn.run"),
    ):
        main([])

    mock_ensure_db.assert_called_once_with("postgresql+psycopg://postgres:postgres@localhost:5432/myblog")
    mock_upgrade.assert_called_once()
