from app.models import Post
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


def test_edit_post_page_renders_existing_data(client, logged_in_admin, seeded_post) -> None:
    response = client.get(f"/admin/posts/{seeded_post.id}/edit")

    assert response.status_code == 200
    assert "编辑文章" in response.text
    assert "My First Post" in response.text


def test_admin_can_edit_post(client, logged_in_admin, seeded_post, db_session) -> None:
    original_slug = seeded_post.slug

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

    refreshed_post = db_session.get(Post, seeded_post.id)
    assert refreshed_post is not None
    assert refreshed_post.title == "Updated Title"
    assert refreshed_post.summary == "Updated Summary"
    assert refreshed_post.content == "Updated content"
    assert refreshed_post.slug == original_slug
