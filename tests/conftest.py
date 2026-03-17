import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

# CSRF 头常量，所有写接口测试需要携带
CSRF_HEADERS = {"X-Requested-With": "XMLHttpRequest"}


class CsrfTestClient(TestClient):
    """自动为写请求（POST/PUT/PATCH/DELETE）注入 CSRF 头的测试客户端"""

    def _inject_csrf(self, kwargs: dict) -> dict:
        headers = dict(kwargs.get("headers") or {})
        headers.setdefault("X-Requested-With", "XMLHttpRequest")
        kwargs["headers"] = headers
        return kwargs

    def post(self, *args, **kwargs):
        return super().post(*args, **self._inject_csrf(kwargs))

    def put(self, *args, **kwargs):
        return super().put(*args, **self._inject_csrf(kwargs))

    def patch(self, *args, **kwargs):
        return super().patch(*args, **self._inject_csrf(kwargs))

    def delete(self, *args, **kwargs):
        return super().delete(*args, **self._inject_csrf(kwargs))


os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-myblog-unit-tests!"

import app.models  # noqa: E402, F401
from app.core.database_provider import create_app_engine  # noqa: E402
from app.core.db import Base, get_db  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402
from app.models import Category, Post, SiteSettings, Tag  # noqa: E402

# 导入 feed 缓存，用于测试间清理
from app.routes.feed import _feed_cache  # noqa: E402
from app.services.auth_service import build_admin_user  # noqa: E402
from app.services.setup_service import clear_initialized_cache  # noqa: E402

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_app_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db_session(setup_database: None) -> Generator[Session, None, None]:
    """每个测试前清空所有表数据（保留表结构），比 drop_all/create_all 更快"""
    clear_initialized_cache()
    # 清除 RSS feed 缓存，避免测试间互相干扰
    _feed_cache.clear()
    # 重置登录限流器，避免测试间累积触发限流
    from app.core.rate_limiter import login_limiter

    login_limiter._attempts.clear()
    session = TestingSessionLocal()
    try:
        # 按外键依赖顺序清空数据，避免 drop_all/create_all 的开销
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[CsrfTestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with CsrfTestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()


@pytest.fixture()
def initialized_site(db_session: Session) -> SiteSettings:
    settings = SiteSettings(
        blog_title="测试博客",
        author_name="admin",
        author_bio="",
        author_email="",
        author_avatar="",
        author_link="",
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
def logged_in_admin(client: CsrfTestClient, initialized_site: SiteSettings, admin_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "secret123"},
        headers=CSRF_HEADERS,
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
def seeded_post(db_session: Session, seeded_category: Category, seeded_tags: list[Tag]) -> Post:
    post = Post(
        title="My First Post",
        slug="my-first-post",
        summary="Intro",
        content="Hello World",
        category=seeded_category,
        published_at=None,
    )
    for tag in seeded_tags:
        post.tags.append(tag)
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post
