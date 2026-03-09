from app.models import Category, Post
from app.schemas.post import PostCreate
from app.services.post_service import build_post


def test_build_post_generates_slug() -> None:
    data = PostCreate(
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


def test_admin_posts_redirects_to_setup_when_uninitialized(client) -> None:
    response = client.get("/admin/posts", follow_redirects=False)

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/setup"


def test_admin_post_list_requires_login(client, initialized_site, admin_user) -> None:
    response = client.get("/admin/posts", follow_redirects=False)

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/admin/login"


def test_admin_post_list_renders_after_login(client, logged_in_admin, seeded_post) -> None:
    response = client.get("/admin/posts")

    assert response.status_code == 200
    assert "文章管理" in response.text
    assert "My First Post" in response.text


def test_admin_new_post_page_renders(client, logged_in_admin, seeded_category, seeded_tags) -> None:
    response = client.get("/admin/posts/new")

    assert response.status_code == 200
    assert "新建文章" in response.text
    assert "Python" in response.text
    assert "FastAPI" in response.text


def test_admin_can_create_post(client, logged_in_admin, seeded_category, seeded_tags) -> None:
    response = client.post(
        "/admin/posts/new",
        data={
            "title": "我的第一篇博客",
            "summary": "Intro",
            "content": "Hello World",
            "category_id": str(seeded_category.id),
            "tag_ids": [str(tag.id) for tag in seeded_tags],
        },
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/admin/posts"

    page = client.get("/admin/posts")
    assert page.status_code == 200
    assert "我的第一篇博客" in page.text
    assert "wo-de-di-yi-pian-bo-ke" in page.text


def test_admin_can_create_post_without_tags(client, logged_in_admin, seeded_category, seeded_tags) -> None:
    response = client.post(
        "/admin/posts/new",
        data={
            "title": "无标签文章",
            "summary": "Intro",
            "content": "Hello World",
            "category_id": str(seeded_category.id),
        },
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/admin/posts"


def test_edit_post_page_renders_existing_data(client, logged_in_admin, seeded_post) -> None:
    response = client.get(f"/admin/posts/{seeded_post.id}/edit")

    assert response.status_code == 200
    assert "编辑文章" in response.text
    assert "My First Post" in response.text


def test_admin_can_edit_post(client, logged_in_admin, seeded_post) -> None:
    response = client.post(
        f"/admin/posts/{seeded_post.id}/edit",
        data={
            "title": "Updated Title",
            "summary": "Updated Summary",
            "content": "Updated content",
            "category_id": str(seeded_post.category_id),
            "tag_ids": [],
        },
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/admin/posts"

    page = client.get("/admin/posts")
    assert page.status_code == 200
    assert "Updated Title" in page.text


def test_admin_create_post_uses_default_category_when_missing(client, logged_in_admin, db_session) -> None:
    response = client.post(
        "/admin/posts/new",
        data={
            "title": "标题",
            "summary": "摘要",
            "content": "内容",
            "category_id": "",
        },
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/admin/posts"

    created_post = db_session.query(Post).filter(Post.title == "标题").one()
    default_category = db_session.query(Category).filter(Category.slug == "default").one()
    assert created_post.category_id == default_category.id


def test_admin_can_publish_post(client, logged_in_admin, seeded_post, db_session) -> None:
    response = client.post(f"/admin/posts/{seeded_post.id}/publish", follow_redirects=False)

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/admin/posts"

    db_session.refresh(seeded_post)
    assert seeded_post.published_at is not None


def test_admin_can_unpublish_post(client, logged_in_admin, seeded_post, db_session) -> None:
    client.post(f"/admin/posts/{seeded_post.id}/publish", follow_redirects=False)

    response = client.post(f"/admin/posts/{seeded_post.id}/unpublish", follow_redirects=False)

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/admin/posts"

    db_session.refresh(seeded_post)
    assert seeded_post.published_at is None


def test_admin_publish_post_requires_login(client, initialized_site, admin_user, seeded_post) -> None:
    response = client.post(f"/admin/posts/{seeded_post.id}/publish", follow_redirects=False)

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/admin/login"


def test_admin_unpublish_post_requires_login(client, initialized_site, admin_user, seeded_post) -> None:
    response = client.post(f"/admin/posts/{seeded_post.id}/unpublish", follow_redirects=False)

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/admin/login"


def test_admin_publish_post_returns_404_for_missing_post(client, logged_in_admin) -> None:
    response = client.post("/admin/posts/999999/publish", follow_redirects=False)

    assert response.status_code == 404


def test_admin_unpublish_post_returns_404_for_missing_post(client, logged_in_admin) -> None:
    response = client.post("/admin/posts/999999/unpublish", follow_redirects=False)

    assert response.status_code == 404


def test_edit_post_page_returns_404_for_missing_post(client, logged_in_admin) -> None:
    response = client.get("/admin/posts/999999/edit")
    assert response.status_code == 404


def test_admin_edit_post_returns_404_for_missing_post(client, logged_in_admin, seeded_post) -> None:
    response = client.post(
        "/admin/posts/999999/edit",
        data={
            "title": "Updated Title",
            "summary": "Updated Summary",
            "content": "Updated content",
            "category_id": str(seeded_post.category_id),
            "tag_ids": [],
        },
    )

    assert response.status_code == 404
