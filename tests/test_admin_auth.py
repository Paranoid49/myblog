from pathlib import Path
from unittest.mock import patch

from app.core.security import hash_password, verify_password
from app.services.auth_service import build_admin_user


def test_password_hash_and_verify() -> None:
    password = "secret123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True


def test_build_admin_user_hashes_password() -> None:
    user = build_admin_user("admin", "secret123")
    assert user.username == "admin"
    assert user.password_hash != "secret123"
    assert verify_password("secret123", user.password_hash) is True


def test_create_admin_script_exists() -> None:
    assert Path("scripts/create_admin.py").exists()


def test_setup_page_is_available_when_target_database_does_not_exist(client) -> None:
    with patch("app.routes.setup.database_exists", return_value=False):
        response = client.get("/setup")

    assert response.status_code == 200
    assert "博客标题" in response.text


def test_setup_submission_bootstraps_database_before_migration_and_initialization(client, db_session) -> None:
    with (
        patch("app.routes.setup.should_bootstrap_database", return_value=True),
        patch("app.routes.setup.ensure_database_exists") as mock_bootstrap,
        patch("app.routes.setup.upgrade_database") as mock_upgrade,
        patch("app.routes.setup.create_session") as mock_create_session,
        patch("app.routes.setup.initialize_site") as mock_initialize,
    ):
        mock_create_session.return_value.__enter__.return_value = db_session
        mock_initialize.return_value.id = 1

        response = client.post(
            "/setup",
            data={
                "blog_title": "我的博客",
                "username": "admin",
                "password": "secret123",
                "confirm_password": "secret123",
            },
            follow_redirects=False,
        )

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/admin/posts"
    mock_bootstrap.assert_called_once()
    mock_upgrade.assert_called_once()
    mock_create_session.assert_called()
    mock_initialize.assert_called_once()


def test_setup_submission_shows_generic_error_when_bootstrap_fails(client) -> None:
    from app.services.database_bootstrap_service import DatabaseBootstrapError

    with (
        patch("app.routes.setup.should_bootstrap_database", return_value=True),
        patch("app.routes.setup.ensure_database_exists", side_effect=DatabaseBootstrapError()),
    ):
        response = client.post(
            "/setup",
            data={
                "blog_title": "我的博客",
                "username": "admin",
                "password": "secret123",
                "confirm_password": "secret123",
            },
        )

    assert response.status_code == 400
    assert "初始化失败，请检查数据库配置后重试" in response.text


def test_setup_submission_does_not_bootstrap_when_password_mismatch(client) -> None:
    with patch("app.routes.setup.ensure_database_exists") as mock_bootstrap:
        response = client.post(
            "/setup",
            data={
                "blog_title": "我的博客",
                "username": "admin",
                "password": "secret123",
                "confirm_password": "wrong",
            },
        )

    assert response.status_code == 400
    mock_bootstrap.assert_not_called()


def test_setup_submission_initializes_site_and_redirects_to_admin_posts(client, db_session) -> None:
    with patch("app.routes.setup.upgrade_database"):
        response = client.post(
            "/setup",
            data={
                "blog_title": "我的博客",
                "username": "admin",
                "password": "secret123",
                "confirm_password": "secret123",
            },
            follow_redirects=False,
        )

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/admin/posts"


def test_setup_submission_rejects_password_mismatch(client) -> None:
    response = client.post(
        "/setup",
        data={
            "blog_title": "我的博客",
            "username": "admin",
            "password": "secret123",
            "confirm_password": "wrong",
        },
    )

    assert response.status_code == 400
    assert "两次密码不一致" in response.text


def test_setup_submission_redirects_home_when_already_initialized(client, db_session) -> None:
    from app.models import SiteSettings
    from app.services.auth_service import build_admin_user

    db_session.add(SiteSettings(blog_title="My Blog"))
    db_session.add(build_admin_user("admin", "secret123"))
    db_session.commit()

    response = client.post(
        "/setup",
        data={
            "blog_title": "Another Blog",
            "username": "root",
            "password": "secret123",
            "confirm_password": "secret123",
        },
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/"


def test_setup_page_is_available_when_uninitialized(client) -> None:
    response = client.get("/setup")
    assert response.status_code == 200
    assert "博客标题" in response.text
    assert "管理员用户名" in response.text


def test_setup_page_redirects_home_when_initialized(client, db_session) -> None:
    from app.models import SiteSettings
    from app.services.auth_service import build_admin_user

    db_session.add(SiteSettings(blog_title="我的博客"))
    db_session.add(build_admin_user("admin", "secret123"))
    db_session.commit()

    response = client.get("/setup", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/"


def test_admin_login_redirects_to_setup_when_uninitialized(client) -> None:
    response = client.get("/admin/login", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/setup"


def test_admin_login_page_renders(client, initialized_site, admin_user) -> None:
    response = client.get("/admin/login")
    assert response.status_code == 200
    assert "登录" in response.text


def test_admin_login_sets_session(client, initialized_site, admin_user) -> None:
    response = client.post(
        "/admin/login",
        data={"username": "admin", "password": "secret123"},
        follow_redirects=False,
    )
    assert response.status_code in (302, 303)


def test_admin_logout_clears_session(client) -> None:
    response = client.get("/admin/logout", follow_redirects=False)
    assert response.status_code == 302
