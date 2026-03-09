from app.models import Category


def test_api_list_posts_returns_published_only(client, initialized_site, admin_user, seeded_post, db_session) -> None:
    seeded_post.published_at = seeded_post.created_at
    db_session.commit()

    response = client.get("/api/v1/posts")

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["message"] == "ok"
    assert isinstance(payload["data"], list)
    assert len(payload["data"]) == 1
    assert payload["data"][0]["title"] == "My First Post"


def test_api_create_admin_post_requires_login(client, initialized_site, admin_user) -> None:
    response = client.post(
        "/api/v1/admin/posts",
        json={
            "title": "API 文章",
            "summary": "摘要",
            "content": "正文",
            "category_id": None,
            "tag_ids": [],
        },
    )

    assert response.status_code == 401


def test_api_create_admin_post_success(client, logged_in_admin, db_session) -> None:
    category = Category(name="Python", slug="python")
    db_session.add(category)
    db_session.commit()

    response = client.post(
        "/api/v1/admin/posts",
        json={
            "title": "API 文章",
            "summary": "摘要",
            "content": "正文",
            "category_id": category.id,
            "tag_ids": [],
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["code"] == 0
    assert payload["message"] == "ok"
    assert payload["data"]["title"] == "API 文章"
    assert payload["data"]["slug"] == "api-wen-zhang"


def test_api_create_admin_post_uses_default_category_when_missing(client, logged_in_admin, db_session) -> None:
    response = client.post(
        "/api/v1/admin/posts",
        json={
            "title": "默认分类API",
            "summary": "摘要",
            "content": "正文",
            "tag_ids": [],
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["data"]["category_id"] is not None
