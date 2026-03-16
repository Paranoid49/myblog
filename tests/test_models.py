from app.core.db import Base
from app.models import Category, Post, Tag, User


def test_models_have_expected_tablenames() -> None:
    assert User.__tablename__ == "users"
    assert Category.__tablename__ == "categories"
    assert Tag.__tablename__ == "tags"
    assert Post.__tablename__ == "posts"


def test_base_metadata_contains_blog_tables() -> None:
    table_names = set(Base.metadata.tables.keys())
    assert {"users", "categories", "tags", "posts", "post_tags", "site_settings"}.issubset(table_names)
