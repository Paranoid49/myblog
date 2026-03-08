from app.models import Category, Post, Tag, User


def test_models_have_expected_tablenames() -> None:
    assert User.__tablename__ == "users"
    assert Category.__tablename__ == "categories"
    assert Tag.__tablename__ == "tags"
    assert Post.__tablename__ == "posts"
