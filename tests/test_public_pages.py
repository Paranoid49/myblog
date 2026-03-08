from unittest.mock import patch


def test_home_redirects_to_setup_when_target_database_does_not_exist(client) -> None:
    with patch("app.routes.public.database_exists", return_value=False):
        response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/setup"


def test_home_displays_database_blog_title_when_initialized(client, db_session) -> None:
    from app.models import SiteSettings
    from app.services.auth_service import build_admin_user

    db_session.add(SiteSettings(blog_title="调试标题-123"))
    db_session.add(build_admin_user("admin", "secret123"))
    db_session.commit()

    response = client.get("/")
    assert response.status_code == 200
    assert "调试标题-123" in response.text


def test_home_redirects_to_setup_when_uninitialized(client) -> None:
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/setup"


def test_homepage_returns_html(client, initialized_site) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_homepage_lists_posts(client, initialized_site, admin_user, seeded_post) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "My First Post" in response.text


def test_homepage_handles_empty_posts(client, initialized_site, admin_user) -> None:
    response = client.get("/")
    assert "暂无文章" in response.text


def test_post_detail_uses_slug_route(client, seeded_post) -> None:
    response = client.get("/posts/my-first-post")
    assert response.status_code == 200
    assert "My First Post" in response.text


def test_post_detail_returns_404_for_missing_slug(client) -> None:
    response = client.get("/posts/not-found")
    assert response.status_code == 404


def test_category_page_lists_posts(client, seeded_post) -> None:
    response = client.get("/categories/python")
    assert response.status_code == 200
    assert "My First Post" in response.text


def test_tag_page_lists_posts(client, seeded_post) -> None:
    response = client.get("/tags/fastapi")
    assert response.status_code == 200
    assert "My First Post" in response.text
