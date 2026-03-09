from pathlib import Path

from app.core.config import settings
from app.routes import setup


def test_settings_load_env_file_from_project_root() -> None:
    expected_env_path = Path(__file__).resolve().parents[1] / ".env"

    assert settings.model_config.get("env_file") == expected_env_path


def test_setup_route_templates_use_absolute_existing_directory() -> None:
    template_dir = Path(setup.templates.env.loader.searchpath[0])
    assert template_dir.is_absolute()
    assert template_dir.exists()
    assert template_dir.name == "templates"
