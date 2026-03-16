"""RSS Feed 接口测试"""


def test_feed_returns_rss_xml(client, initialized_site, admin_user):
    """feed.xml 返回 RSS XML 格式"""
    response = client.get("/feed.xml")
    assert response.status_code == 200
    assert "application/rss+xml" in response.headers.get("content-type", "")
    assert "<rss" in response.text
    assert "<channel>" in response.text


def test_feed_contains_published_posts_only(client, logged_in_admin, seeded_category):
    """feed 仅包含已发布文章"""
    # 创建并发布文章
    resp = client.post("/api/v1/admin/posts", json={
        "title": "Feed 测试文章",
        "content": "内容",
        "category_id": seeded_category.id,
        "tag_ids": [],
    })
    post_id = resp.json()["data"]["id"]
    client.post(f"/api/v1/admin/posts/{post_id}/publish")

    # 创建但不发布的文章
    client.post("/api/v1/admin/posts", json={
        "title": "草稿文章",
        "content": "不应出现",
        "category_id": seeded_category.id,
        "tag_ids": [],
    })

    response = client.get("/feed.xml")
    assert "Feed 测试文章" in response.text
    assert "草稿文章" not in response.text
