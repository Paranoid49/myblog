from datetime import UTC, datetime, timedelta

from app.models import Category, Post, Tag
from app.services.taxonomy_service import (
    get_published_posts_by_category,
    get_published_posts_by_tag,
)


def test_get_published_posts_by_category_returns_none_for_missing(db_session) -> None:
    category, posts, total = get_published_posts_by_category(db_session, "missing")
    assert category is None
    assert posts == []
    assert total == 0


def test_get_published_posts_by_category_returns_published_posts(db_session) -> None:
    category = Category(name="Python", slug="python")
    published = Post(
        title="Published",
        slug="published",
        summary="S",
        content="C",
        category=category,
        published_at=datetime.now(UTC),
    )
    draft = Post(title="Draft", slug="draft", summary="S", content="C", category=category)
    db_session.add_all([category, published, draft])
    db_session.commit()

    result_cat, posts, total = get_published_posts_by_category(db_session, "python")

    assert result_cat is not None
    assert result_cat.slug == "python"
    assert total == 1
    assert [p.slug for p in posts] == ["published"]


def test_get_published_posts_by_tag_returns_none_for_missing(db_session) -> None:
    tag, posts, total = get_published_posts_by_tag(db_session, "missing")
    assert tag is None
    assert posts == []
    assert total == 0


def test_get_published_posts_by_tag_returns_published_posts(db_session) -> None:
    category = Category(name="Python", slug="python")
    tag = Tag(name="FastAPI", slug="fastapi")
    published = Post(
        title="Published",
        slug="published",
        summary="S",
        content="C",
        category=category,
        published_at=datetime.now(UTC),
    )
    published.tags.append(tag)
    draft = Post(title="Draft", slug="draft", summary="S", content="C", category=category)
    draft.tags.append(tag)
    db_session.add_all([category, tag, published, draft])
    db_session.commit()

    result_tag, posts, total = get_published_posts_by_tag(db_session, "fastapi")

    assert result_tag is not None
    assert result_tag.slug == "fastapi"
    assert total == 1
    assert [p.slug for p in posts] == ["published"]
