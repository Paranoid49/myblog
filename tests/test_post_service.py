from datetime import datetime, timedelta, timezone

from app.models import Category, Post, Tag
from app.schemas.post import PostCreate
from app.services.post_service import (
    build_post,
    ensure_unique_slug,
    get_post_by_slug,
    list_published_posts,
    slugify,
    update_post,
)


def test_slugify_converts_title_to_url_slug() -> None:
    assert slugify("Hello World FastAPI") == "hello-world-fastapi"


def test_slugify_converts_chinese_title_to_pinyin() -> None:
    assert slugify("我的第一篇博客") == "wo-de-di-yi-pian-bo-ke"


def test_slugify_handles_mixed_chinese_english_and_numbers() -> None:
    assert slugify("FastAPI 入门教程 2026") == "fastapi-ru-men-jiao-cheng-2026"


def test_slugify_treats_symbols_as_separators() -> None:
    assert slugify("Python & PostgreSQL 实战！") == "python-postgresql-shi-zhan"


def test_slugify_falls_back_to_post_when_slug_is_empty() -> None:
    assert slugify("！！！@@@") == "post"


def test_ensure_unique_slug_adds_suffix() -> None:
    assert ensure_unique_slug("hello-world", {"hello-world", "hello-world-2"}) == "hello-world-3"


def test_ensure_unique_slug_handles_chinese_generated_slug() -> None:
    base_slug = slugify("我的博客")
    assert ensure_unique_slug(base_slug, {"wo-de-bo-ke", "wo-de-bo-ke-2"}) == "wo-de-bo-ke-3"


def test_build_post_applies_unique_slug_when_title_conflicts() -> None:
    data = PostCreate(
        title="My First Post",
        summary="Intro",
        content="Hello",
        category_id=1,
        tag_ids=[],
    )

    post = build_post(data, existing_slugs={"my-first-post", "my-first-post-2"})

    assert post.slug == "my-first-post-3"


def test_update_post_replaces_fields_and_tags(db_session) -> None:
    category_a = Category(name="Python", slug="python")
    category_b = Category(name="FastAPI", slug="fastapi")
    tag_a = Tag(name="Web", slug="web")
    tag_b = Tag(name="API", slug="api")
    post = Post(title="Old", slug="old", summary="S", content="C", category=category_a)
    post.tags = [tag_a]
    db_session.add_all([category_a, category_b, tag_a, tag_b, post])
    db_session.commit()

    data = PostCreate(
        title="New Title",
        summary="New Summary",
        content="New Content",
        category_id=category_b.id,
        tag_ids=[tag_b.id],
    )

    updated = update_post(post, data, [tag_b])

    assert updated.title == "New Title"
    assert updated.summary == "New Summary"
    assert updated.content == "New Content"
    assert updated.category_id == category_b.id
    assert [tag.slug for tag in updated.tags] == ["api"]


def test_list_published_posts_returns_newest_first(db_session) -> None:
    category = Category(name="Python", slug="python")
    old_post = Post(
        title="Old",
        slug="old",
        summary="Old",
        content="Old",
        category=category,
        created_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    new_post = Post(
        title="New",
        slug="new",
        summary="New",
        content="New",
        category=category,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add_all([category, old_post, new_post])
    db_session.commit()

    posts = list_published_posts(db_session)

    assert [post.slug for post in posts] == ["new", "old"]


def test_get_post_by_slug_returns_none_for_missing_slug(db_session) -> None:
    assert get_post_by_slug(db_session, "not-found") is None


def test_get_post_by_slug_returns_post_for_existing_slug(db_session) -> None:
    category = Category(name="Python", slug="python")
    post = Post(title="Title", slug="existing-slug", summary="S", content="C", category=category)
    db_session.add_all([category, post])
    db_session.commit()

    result = get_post_by_slug(db_session, "existing-slug")

    assert result is not None
    assert result.slug == "existing-slug"
