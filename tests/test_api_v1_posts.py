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


def test_api_post_detail_success(client, initialized_site, admin_user, seeded_post, db_session) -> None:
    seeded_post.published_at = seeded_post.created_at
    db_session.commit()

    response = client.get(f"/api/v1/posts/{seeded_post.slug}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["slug"] == seeded_post.slug


def test_api_post_detail_returns_404_for_draft(client, initialized_site, admin_user, seeded_post) -> None:
    response = client.get(f"/api/v1/posts/{seeded_post.slug}")

    assert response.status_code == 404
    payload = response.json()
    assert payload["code"] == 1404


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
    payload = response.json()
    assert payload["code"] == 1002


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


def test_api_list_admin_posts_requires_login(client, initialized_site, admin_user) -> None:
    response = client.get("/api/v1/admin/posts")

    assert response.status_code == 401
    payload = response.json()
    assert payload["code"] == 1002


def test_api_list_admin_posts_success(client, logged_in_admin, seeded_post) -> None:
    response = client.get("/api/v1/admin/posts")

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert isinstance(payload["data"], list)
    assert len(payload["data"]) >= 1


def test_api_publish_post_success(client, logged_in_admin, seeded_post, db_session) -> None:
    response = client.post(f"/api/v1/admin/posts/{seeded_post.id}/publish")

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["published_at"] is not None


def test_api_unpublish_post_success(client, logged_in_admin, seeded_post, db_session) -> None:
    client.post(f"/api/v1/admin/posts/{seeded_post.id}/publish")

    response = client.post(f"/api/v1/admin/posts/{seeded_post.id}/unpublish")

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["published_at"] is None


def test_api_list_taxonomy_requires_login(client, initialized_site, admin_user) -> None:
    response = client.get("/api/v1/taxonomy")

    assert response.status_code == 401
    payload = response.json()
    assert payload["code"] == 1002


def test_api_list_taxonomy_success(client, logged_in_admin, seeded_category, seeded_tags) -> None:
    response = client.get("/api/v1/taxonomy")

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["categories"][0]["slug"] == "python"
    assert payload["data"]["tags"][0]["slug"] == "fastapi"


def test_api_create_category_success(client, logged_in_admin) -> None:
    response = client.post("/api/v1/admin/categories", json={"name": "数据库"})

    assert response.status_code == 201
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["slug"] == "shu-ju-ku"


def test_api_create_tag_success(client, logged_in_admin) -> None:
    response = client.post("/api/v1/admin/tags", json={"name": "后端"})

    assert response.status_code == 201
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["slug"] == "hou-duan"


def test_api_create_category_rejects_duplicate(client, logged_in_admin, seeded_category) -> None:
    response = client.post("/api/v1/admin/categories", json={"name": "python"})

    assert response.status_code == 409
    payload = response.json()
    assert payload["code"] == 1409


def test_api_create_tag_rejects_duplicate(client, logged_in_admin, seeded_tags) -> None:
    response = client.post("/api/v1/admin/tags", json={"name": "FastAPI"})

    assert response.status_code == 409
    payload = response.json()
    assert payload["code"] == 1410
