from pathlib import Path

import pytest

from app.models import Category, Post

_FRONTEND_DIST = Path(__file__).resolve().parents[1] / "frontend" / "dist"
_skip_no_dist = pytest.mark.skipif(not _FRONTEND_DIST.exists(), reason="frontend/dist 未构建")


@_skip_no_dist
def test_admin_routes_are_served_by_frontend_spa(client, initialized_site, admin_user) -> None:
    response = client.get("/admin/posts")

    assert response.status_code == 200
    assert '<div id="root"></div>' in response.text


def test_admin_create_post_uses_default_category_when_missing(client, logged_in_admin, db_session) -> None:
    response = client.post(
        "/api/v1/admin/posts",
        json={
            "title": "标题",
            "summary": "摘要",
            "content": "内容",
            "category_id": None,
            "tag_ids": [],
        },
    )

    assert response.status_code == 201

    created_post = db_session.query(Post).filter(Post.title == "标题").one()
    default_category = db_session.query(Category).filter(Category.slug == "default").one()
    assert created_post.category_id == default_category.id


def test_admin_can_publish_post(client, logged_in_admin, seeded_post, db_session) -> None:
    response = client.post(f"/api/v1/admin/posts/{seeded_post.id}/publish")

    assert response.status_code == 200

    db_session.refresh(seeded_post)
    assert seeded_post.published_at is not None


def test_admin_can_unpublish_post(client, logged_in_admin, seeded_post, db_session) -> None:
    client.post(f"/api/v1/admin/posts/{seeded_post.id}/publish")

    response = client.post(f"/api/v1/admin/posts/{seeded_post.id}/unpublish")

    assert response.status_code == 200

    db_session.refresh(seeded_post)
    assert seeded_post.published_at is None


def test_admin_publish_post_requires_login(client, initialized_site, admin_user, seeded_post) -> None:
    response = client.post(f"/api/v1/admin/posts/{seeded_post.id}/publish")

    assert response.status_code == 401


def test_admin_unpublish_post_requires_login(client, initialized_site, admin_user, seeded_post) -> None:
    response = client.post(f"/api/v1/admin/posts/{seeded_post.id}/unpublish")

    assert response.status_code == 401


def test_admin_publish_post_returns_404_for_missing_post(client, logged_in_admin) -> None:
    response = client.post("/api/v1/admin/posts/999999/publish")

    assert response.status_code == 404


def test_admin_unpublish_post_returns_404_for_missing_post(client, logged_in_admin) -> None:
    response = client.post("/api/v1/admin/posts/999999/unpublish")

    assert response.status_code == 404


def test_admin_can_delete_post(client, logged_in_admin, seeded_category):
    """管理员可以删除文章"""
    resp = client.post(
        "/api/v1/admin/posts",
        json={
            "title": "待删除文章",
            "content": "会被删除",
            "category_id": seeded_category.id,
            "tag_ids": [],
        },
    )
    post_id = resp.json()["data"]["id"]
    delete_resp = client.delete(f"/api/v1/admin/posts/{post_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["code"] == 0


def test_admin_delete_post_returns_404_for_missing(client, logged_in_admin):
    """删除不存在的文章返回 404"""
    resp = client.delete("/api/v1/admin/posts/99999")
    assert resp.status_code == 404
