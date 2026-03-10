from pathlib import Path
from unittest.mock import patch

from app.core.security import hash_password, verify_password
from app.models import User
from app.services.auth_service import authenticate_user, build_admin_user


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


def test_authenticate_user_returns_user_for_valid_credentials(db_session) -> None:
    user = build_admin_user("admin", "secret123")
    db_session.add(user)
    db_session.commit()

    result = authenticate_user(db_session, "admin", "secret123")

    assert result is not None
    assert result.username == "admin"


def test_authenticate_user_returns_none_for_wrong_password(db_session) -> None:
    user = build_admin_user("admin", "secret123")
    db_session.add(user)
    db_session.commit()

    assert authenticate_user(db_session, "admin", "wrong") is None


def test_authenticate_user_returns_none_for_inactive_user(db_session) -> None:
    user = User(username="admin", password_hash=hash_password("secret123"), is_active=False)
    db_session.add(user)
    db_session.commit()

    assert authenticate_user(db_session, "admin", "secret123") is None


def test_authenticate_user_returns_none_for_missing_user(db_session) -> None:
    assert authenticate_user(db_session, "missing", "secret123") is None


def test_create_admin_script_exists() -> None:
    assert Path("scripts/create_admin.py").exists()


# ===== Setup API Tests =====

def test_setup_status_returns_not_initialized(client) -> None:
    response = client.get("/api/v1/setup/status")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["initialized"] is False


def test_setup_status_returns_initialized(client, initialized_site, admin_user) -> None:
    response = client.get("/api/v1/setup/status")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["initialized"] is True


def test_setup_api_initializes_site(client, db_session) -> None:
    with patch("app.routes.api_v1_setup.upgrade_database"):
        response = client.post(
            "/api/v1/setup",
            json={
                "blog_title": "我的博客",
                "username": "admin",
                "password": "secret123",
                "confirm_password": "secret123",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["username"] == "admin"


def test_setup_api_rejects_password_mismatch(client) -> None:
    response = client.post(
        "/api/v1/setup",
        json={
            "blog_title": "我的博客",
            "username": "admin",
            "password": "secret123",
            "confirm_password": "wrong",
        },
    )

    assert response.status_code == 400
    assert response.json()["code"] == 2001


def test_setup_api_rejects_already_initialized(client, initialized_site, admin_user) -> None:
    with patch("app.routes.api_v1_setup.upgrade_database"):
        response = client.post(
            "/api/v1/setup",
            json={
                "blog_title": "Another Blog",
                "username": "root",
                "password": "secret123",
                "confirm_password": "secret123",
            },
        )

    assert response.status_code == 409
    assert response.json()["code"] == 2004


def test_setup_page_is_served_by_spa(client) -> None:
    response = client.get("/setup")
    assert response.status_code == 200
    assert '<div id="root"></div>' in response.text


def test_setup_page_is_served_by_spa_when_initialized(client, initialized_site, admin_user) -> None:
    response = client.get("/setup")
    assert response.status_code == 200
    assert '<div id="root"></div>' in response.text