from app.models import Category, Post, Tag
from app.services.taxonomy_service import get_category_by_slug, get_tag_by_slug


def test_get_category_by_slug_returns_none_for_missing_slug(db_session) -> None:
    assert get_category_by_slug(db_session, "missing") is None


def test_get_category_by_slug_returns_category_with_posts(db_session) -> None:
    category = Category(name="Python", slug="python")
    post = Post(title="Hello", slug="hello", summary="S", content="C", category=category)
    db_session.add_all([category, post])
    db_session.commit()

    result = get_category_by_slug(db_session, "python")

    assert result is not None
    assert result.slug == "python"
    assert [item.slug for item in result.posts] == ["hello"]


def test_get_tag_by_slug_returns_none_for_missing_slug(db_session) -> None:
    assert get_tag_by_slug(db_session, "missing") is None


def test_get_tag_by_slug_returns_tag_with_posts(db_session) -> None:
    category = Category(name="Python", slug="python")
    tag = Tag(name="FastAPI", slug="fastapi")
    post = Post(title="Hello", slug="hello", summary="S", content="C", category=category)
    post.tags.append(tag)
    db_session.add_all([category, tag, post])
    db_session.commit()

    result = get_tag_by_slug(db_session, "fastapi")

    assert result is not None
    assert result.slug == "fastapi"
    assert [item.slug for item in result.posts] == ["hello"]
