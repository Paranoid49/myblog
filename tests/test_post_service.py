from app.services.post_service import ensure_unique_slug, slugify


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
