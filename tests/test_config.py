from pathlib import Path

from app.core.config import DEFAULT_SQLITE_URL, settings


def test_settings_load_env_file_from_project_root() -> None:
    expected_env_path = Path(__file__).resolve().parents[1] / ".env"

    assert settings.model_config.get("env_file") == expected_env_path


def test_settings_use_sqlite_as_default_database() -> None:
    assert DEFAULT_SQLITE_URL.startswith("sqlite:///")
    assert settings.__class__.model_fields["database_url"].default == DEFAULT_SQLITE_URL


def test_frontend_dist_exists() -> None:
    dist_dir = Path(__file__).resolve().parents[1] / "frontend" / "dist"
    assert dist_dir.exists(), "frontend/dist should exist (run npm run build)"
    assert (dist_dir / "index.html").exists(), "frontend/dist/index.html should exist"
