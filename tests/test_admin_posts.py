from app.models import Category, Post
from app.services.post_service import PostCreatePayload, build_post


def test_build_post_generates_slug() -> None:
    data = PostCreatePayload(
        title="My First Post",
        summary="Intro",
        content="Hello",
        category_id=1,
        tag_ids=[],
    )

    post = build_post(data, existing_slugs=set())

    assert post.slug == "my-first-post"
    assert post.title == "My First Post"
    assert post.category_id == 1


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
