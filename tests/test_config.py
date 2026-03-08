from pathlib import Path

from app.core.config import settings
from app.routes import admin_auth, admin_posts, public, setup


def test_settings_load_env_file_from_project_root() -> None:
    expected_env_path = Path(__file__).resolve().parents[1] / ".env"

    assert settings.model_config.get("env_file") == expected_env_path


def test_route_templates_use_absolute_existing_directory() -> None:
    route_templates = [
        public.templates,
        setup.templates,
        admin_auth.templates,
        admin_posts.templates,
    ]

    for template in route_templates:
        template_dir = Path(template.env.loader.searchpath[0])
        assert template_dir.is_absolute()
        assert template_dir.exists()
        assert template_dir.name == "templates"
