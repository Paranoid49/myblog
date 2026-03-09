def test_minimal_flow_setup_login_create_publish_and_home_visible(client, db_session) -> None:
    from app.models import Category
    from app.services.setup_service import initialize_site

    initialize_site(db_session, blog_title="我的博客", username="admin", password="secret123")

    login = client.post(
        "/admin/login",
        data={"username": "admin", "password": "secret123"},
        follow_redirects=False,
    )
    assert login.status_code in (302, 303)

    category = Category(name="Python", slug="python")
    db_session.add(category)
    db_session.commit()

    create_resp = client.post(
        "/admin/posts/new",
        data={
            "title": "E2E 文章",
            "summary": "摘要",
            "content": "正文",
            "category_id": str(category.id),
        },
        follow_redirects=False,
    )
    assert create_resp.status_code in (302, 303)

    posts_page = client.get("/admin/posts")
    assert "E2E 文章" in posts_page.text

    # 最后一篇就是刚创建的文章（列表按创建时间倒序）
    import re

    match = re.search(r"/admin/posts/(\d+)/publish", posts_page.text)
    assert match is not None
    post_id = int(match.group(1))

    publish_resp = client.post(f"/admin/posts/{post_id}/publish", follow_redirects=False)
    assert publish_resp.status_code in (302, 303)

    home = client.get("/")
    assert home.status_code == 200
    assert "E2E 文章" in home.text
