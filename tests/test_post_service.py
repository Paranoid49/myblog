from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.models import Category, Post, Tag
from app.schemas.post import ImportMarkdownRequest
from app.services.post_service import (
    PostCreatePayload,
    build_markdown_export,
    build_post,
    build_post_from_import_markdown,
    create_post,
    ensure_unique_slug,
    extract_markdown_title,
    get_post_by_slug,
    get_post_or_raise,
    list_admin_posts,
    list_published_posts,
    PostNotFoundError,
    publish_post,
    unpublish_post,
    update_post,
    _build_admin_post_list_query,
)
from app.utils.text import slugify


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
    data = PostCreatePayload(
        title="My First Post",
        summary="Intro",
        content="Hello",
        category_id=1,
        tag_ids=[],
    )

    post = build_post(data, existing_slugs={"my-first-post", "my-first-post-2"})

    assert post.slug == "my-first-post-3"


def test_extract_markdown_title_prefers_h1() -> None:
    markdown = "前言\n# 正式标题\n\n正文"

    assert extract_markdown_title(markdown) == "正式标题"


def test_extract_markdown_title_falls_back_to_first_non_blank_line() -> None:
    markdown = "\n\n第一行内容\n第二行内容"

    assert extract_markdown_title(markdown) == "第一行内容"


def test_build_markdown_export_includes_title_and_content() -> None:
    post = Post(title="导出标题", slug="dao-chu-biao-ti", summary="S", content="正文内容", category_id=1)

    result = build_markdown_export(post)

    assert result == {
        "filename": "dao-chu-biao-ti.md",
        "markdown": "# 导出标题\n\n正文内容",
    }


def test_build_admin_post_list_query_applies_filters() -> None:
    stmt = _build_admin_post_list_query(category_id=1, tag_id=2)

    compiled = str(stmt)
    assert "posts.category_id = :category_id_1" in compiled
    assert "tags.id = :id_1" in compiled


def test_build_post_from_import_markdown_uses_default_category(db_session) -> None:
    payload = ImportMarkdownRequest(markdown="# 导入标题\n\n正文内容", category_id=None, tag_ids=[])

    data, tags = build_post_from_import_markdown(db_session, payload)

    default_category_id = db_session.execute(select(Category.id).where(Category.slug == "default")).scalar_one()
    assert data.title == "导入标题"
    assert data.content == payload.markdown
    assert data.category_id == default_category_id
    assert tags == []


def test_create_post_applies_unique_slug_and_tags(db_session) -> None:
    category = Category(name="Python", slug="python")
    existing = Post(title="已存在", slug="my-post", summary="S", content="C", category=category)
    tag = Tag(name="FastAPI", slug="fastapi")
    db_session.add_all([category, existing, tag])
    db_session.commit()

    data = PostCreatePayload(
        title="My Post",
        summary="摘要",
        content="正文",
        category_id=category.id,
        tag_ids=[tag.id],
    )

    post = create_post(db_session, data, [tag])

    assert post.slug == "my-post-2"
    assert post.category_id == category.id
    assert [item.slug for item in post.tags] == ["fastapi"]


def test_update_post_replaces_fields_and_tags(db_session) -> None:
    category_a = Category(name="Python", slug="python")
    category_b = Category(name="FastAPI", slug="fastapi")
    tag_a = Tag(name="Web", slug="web")
    tag_b = Tag(name="API", slug="api")
    post = Post(title="Old", slug="old", summary="S", content="C", category=category_a)
    post.tags = [tag_a]
    db_session.add_all([category_a, category_b, tag_a, tag_b, post])
    db_session.commit()

    data = PostCreatePayload(
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


def test_publish_post_sets_published_at() -> None:
    post = Post(title="Draft", slug="draft", summary="S", content="C", category_id=1)

    publish_post(post)

    assert post.published_at is not None


def test_unpublish_post_clears_published_at() -> None:
    post = Post(
        title="Published",
        slug="published",
        summary="S",
        content="C",
        category_id=1,
        published_at=datetime.now(timezone.utc),
    )

    unpublish_post(post)

    assert post.published_at is None


def test_list_published_posts_returns_latest_published_first(db_session) -> None:
    category = Category(name="Python", slug="python")
    draft_post = Post(
        title="Draft",
        slug="draft",
        summary="Draft",
        content="Draft",
        category=category,
        published_at=None,
    )
    old_post = Post(
        title="Old",
        slug="old",
        summary="Old",
        content="Old",
        category=category,
        published_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    new_post = Post(
        title="New",
        slug="new",
        summary="New",
        content="New",
        category=category,
        published_at=datetime.now(timezone.utc),
    )
    db_session.add_all([category, draft_post, old_post, new_post])
    db_session.commit()

    posts, total = list_published_posts(db_session)

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
