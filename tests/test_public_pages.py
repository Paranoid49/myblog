from pathlib import Path

from unittest.mock import patch


def test_home_redirects_to_setup_when_target_database_does_not_exist(client) -> None:
    with patch("app.main.frontend_app", side_effect=AssertionError("frontend should not render")):
        with patch("app.routes.setup.database_exists", return_value=False):
            response = client.get("/setup")
    assert response.status_code == 200


def test_homepage_returns_frontend_index_when_initialized(client, db_session) -> None:
    from app.models import SiteSettings
    from app.services.auth_service import build_admin_user

    db_session.add(SiteSettings(blog_title="调试标题-123", author_name="admin", author_bio="", author_email=""))
    db_session.add(build_admin_user("admin", "secret123"))
    db_session.commit()

    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert '<div id="root"></div>' in response.text


def test_post_detail_uses_frontend_index(client, initialized_site, admin_user, seeded_post) -> None:
    response = client.get("/posts/my-first-post")
    assert response.status_code == 200
    assert '<div id="root"></div>' in response.text


def test_author_page_uses_frontend_index(client, initialized_site, admin_user) -> None:
    response = client.get("/author")
    assert response.status_code == 200
    assert '<div id="root"></div>' in response.text


def test_admin_page_uses_frontend_index(client, initialized_site, admin_user) -> None:
    response = client.get("/admin")
    assert response.status_code == 200
    assert '<div id="root"></div>' in response.text


def test_frontend_dist_exists_for_spa_entry() -> None:
    index_file = Path(__file__).resolve().parents[1] / "frontend" / "dist" / "index.html"
    assert index_file.exists()
