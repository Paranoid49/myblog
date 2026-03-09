from unittest.mock import patch


def test_minimal_flow_setup_login_create_publish_and_home_visible(client, db_session) -> None:
    with patch("app.routes.setup.upgrade_database"):
        login_setup = client.post(
            "/setup",
            data={
                "blog_title": "我的博客",
                "username": "admin",
                "password": "secret123",
                "confirm_password": "secret123",
            },
            follow_redirects=False,
        )
    assert login_setup.status_code in (302, 303)
    assert login_setup.headers["location"] == "/admin/posts"

    taxonomy_response = client.post("/api/v1/admin/categories", json={"name": "Python"})
    assert taxonomy_response.status_code == 201
    category_id = taxonomy_response.json()["data"]["id"]

    create_resp = client.post(
        "/api/v1/admin/posts",
        json={
            "title": "E2E 文章",
            "summary": "摘要",
            "content": "# 正文\n\n这是内容",
            "category_id": category_id,
            "tag_ids": [],
        },
    )
    assert create_resp.status_code == 201
    post_id = create_resp.json()["data"]["id"]

    publish_resp = client.post(f"/api/v1/admin/posts/{post_id}/publish")
    assert publish_resp.status_code == 200

    home = client.get("/")
    assert home.status_code == 200
    assert '<div id="root"></div>' in home.text

    list_resp = client.get("/api/v1/posts")
    assert list_resp.status_code == 200
    payload = list_resp.json()
    assert any(item["title"] == "E2E 文章" for item in payload["data"])
