import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key"

import app.models  # noqa: F401
from app.core.db import Base, get_db
from app.main import app as fastapi_app
from app.models import Category, Post, SiteSettings, Tag
from app.services.auth_service import build_admin_user
from app.services.setup_service import clear_initialized_cache

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, future=True, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def test_base_metadata_contains_blog_tables() -> None:
    table_names = set(Base.metadata.tables.keys())
    assert {"users", "categories", "tags", "posts", "post_tags", "site_settings"}.issubset(table_names)


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db_session(setup_database: None) -> Generator[Session, None, None]:
    clear_initialized_cache()  # 清除初始化状态缓存
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()


@pytest.fixture()
def initialized_site(db_session: Session) -> SiteSettings:
    settings = SiteSettings(
        blog_title="测试博客",
        author_name="admin",
        author_bio="",
        author_email="",
    )
    db_session.add(settings)
    db_session.commit()
    db_session.refresh(settings)
    return settings


@pytest.fixture()
def admin_user(db_session: Session):
    user = build_admin_user("admin", "secret123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def logged_in_admin(client: TestClient, initialized_site: SiteSettings, admin_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "secret123"},
        follow_redirects=False,
    )
    assert response.status_code in (200, 302, 303)
    return admin_user


@pytest.fixture()
def seeded_category(db_session: Session) -> Category:
    category = Category(name="Python", slug="python")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture()
def seeded_tags(db_session: Session) -> list[Tag]:
    tag = Tag(name="FastAPI", slug="fastapi")
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    return [tag]


@pytest.fixture()
def seeded_post(db_session: Session) -> Post:
    category = Category(name="Python", slug="python")
    tag = Tag(name="FastAPI", slug="fastapi")
    post = Post(
        title="My First Post",
        slug="my-first-post",
        summary="Intro",
        content="Hello World",
        category=category,
        published_at=None,
    )
    post.tags.append(tag)

    db_session.add_all([category, tag, post])
    db_session.commit()
    db_session.refresh(post)
    return post
