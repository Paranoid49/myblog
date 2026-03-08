from app.services.post_service import ensure_unique_slug, slugify


def test_slugify_converts_title_to_url_slug() -> None:
    assert slugify("Hello World FastAPI") == "hello-world-fastapi"


def test_ensure_unique_slug_adds_suffix() -> None:
    assert ensure_unique_slug("hello-world", {"hello-world", "hello-world-2"}) == "hello-world-3"
