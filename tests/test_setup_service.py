from pathlib import Path
from unittest.mock import patch

import pytest

from app.core.config import PROJECT_ROOT
from app.core.db import Base
from app.core.security import verify_password
from app.models import SiteSettings
from app.services.auth_service import build_admin_user
from app.services.migration_service import upgrade_database
from app.services.setup_service import (
    SetupAlreadyInitializedError,
    get_site_settings,
    initialize_site,
    is_initialized,
)


def test_base_metadata_contains_site_settings_table() -> None:
    assert "site_settings" in Base.metadata.tables


def test_site_settings_migration_file_exists() -> None:
    migration = Path("migrations/versions/20260308_add_site_settings.py")
    assert migration.exists()


def test_upgrade_database_calls_alembic_upgrade() -> None:
    with patch("app.services.migration_service.command.upgrade") as mock_upgrade:
        upgrade_database()

    mock_upgrade.assert_called_once()


def test_upgrade_database_uses_project_root_alembic_ini_when_cwd_changes(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    with patch("app.services.migration_service.command.upgrade") as mock_upgrade:
        upgrade_database()

    config = mock_upgrade.call_args[0][0]
    assert Path(config.config_file_name) == PROJECT_ROOT / "alembic.ini"


def test_upgrade_database_uses_absolute_script_location_when_cwd_changes(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    with patch("app.services.migration_service.command.upgrade") as mock_upgrade:
        upgrade_database()

    config = mock_upgrade.call_args[0][0]
    assert Path(config.get_main_option("script_location")) == PROJECT_ROOT / "migrations"


def test_is_initialized_returns_false_when_database_has_no_setup_data(db_session) -> None:
    assert is_initialized(db_session) is False


def test_is_initialized_returns_false_with_only_admin(db_session) -> None:
    db_session.add(build_admin_user("admin", "secret123"))
    db_session.commit()
    assert is_initialized(db_session) is False


def test_is_initialized_returns_false_with_only_site_settings(db_session) -> None:
    db_session.add(SiteSettings(blog_title="My Blog"))
    db_session.commit()
    assert is_initialized(db_session) is False


def test_is_initialized_returns_true_with_site_settings_and_admin(db_session) -> None:
    db_session.add(SiteSettings(blog_title="My Blog"))
    db_session.add(build_admin_user("admin", "secret123"))
    db_session.commit()
    assert is_initialized(db_session) is True


def test_initialize_site_creates_site_settings_and_admin(db_session) -> None:
    user = initialize_site(
        db=db_session,
        blog_title="My Blog",
        username="admin",
        password="secret123",
    )

    db_session.refresh(user)
    settings = db_session.query(SiteSettings).one()
    assert settings.blog_title == "My Blog"
    assert user.username == "admin"
    assert user.password_hash != "secret123"
    assert verify_password("secret123", user.password_hash) is True


def test_initialize_site_rejects_repeat_install(db_session) -> None:
    initialize_site(db=db_session, blog_title="My Blog", username="admin", password="secret123")

    with pytest.raises(SetupAlreadyInitializedError):
        initialize_site(db=db_session, blog_title="Other Blog", username="root", password="otherpass")


def test_get_site_settings_returns_none_when_uninitialized(db_session) -> None:
    assert get_site_settings(db_session) is None


def test_get_site_settings_returns_site_settings_after_initialization(db_session) -> None:
    initialize_site(db=db_session, blog_title="My Blog", username="admin", password="secret123")

    settings = get_site_settings(db_session)

    assert settings is not None
    assert settings.blog_title == "My Blog"
