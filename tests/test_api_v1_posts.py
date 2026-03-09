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


def test_api_filter_admin_posts_by_category(client, logged_in_admin, seeded_post) -> None:
    response = client.get(f"/api/v1/admin/posts?category_id={seeded_post.category_id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert isinstance(payload["data"], list)
    assert len(payload["data"]) >= 1


def test_api_update_admin_post_success(client, logged_in_admin, seeded_post) -> None:
    response = client.post(
        f"/api/v1/admin/posts/{seeded_post.id}",
        json={
            "title": "Updated Title",
            "summary": "Updated Summary",
            "content": "# Updated Markdown",
            "category_id": seeded_post.category_id,
            "tag_ids": [tag.id for tag in seeded_post.tags],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["title"] == "Updated Title"
    assert payload["data"]["content"] == "# Updated Markdown"


def test_api_import_markdown_success(client, logged_in_admin) -> None:
    response = client.post(
        "/api/v1/admin/posts/import-markdown",
        json={
            "markdown": "# 导入标题\n\n正文内容",
            "category_id": None,
            "tag_ids": [],
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["title"] == "导入标题"


def test_api_export_markdown_success(client, logged_in_admin, seeded_post) -> None:
    response = client.get(f"/api/v1/admin/posts/{seeded_post.id}/export-markdown")

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["filename"].endswith(".md")
    assert payload["data"]["markdown"].startswith("# ")


def test_api_upload_image_success(client, logged_in_admin) -> None:
    response = client.post(
        "/api/v1/admin/media/images",
        files={"file": ("a.png", b"\x89PNG\r\n\x1a\n", "image/png")},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["content_type"] == "image/png"
    assert payload["data"]["url"].startswith("/static/uploads/")

    from pathlib import Path

    key = payload["data"]["key"]
    (Path(__file__).resolve().parents[1] / "app" / "static" / "uploads" / key).unlink(missing_ok=True)


def test_api_upload_image_rejects_invalid_type(client, logged_in_admin) -> None:
    response = client.post(
        "/api/v1/admin/media/images",
        files={"file": ("a.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == 1411
