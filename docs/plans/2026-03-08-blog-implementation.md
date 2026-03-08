# Blog MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建一个基于 FastAPI + Jinja2 + PostgreSQL 的个人博客首版最小闭环，支持管理员登录、文章发布/编辑、前台文章展示、分类与标签页面。

**Architecture:** 采用单体 SSR 架构。FastAPI 负责路由、鉴权和业务编排，Jinja2 负责前后台页面渲染，PostgreSQL 负责持久化；代码按 core / models / schemas / services / routes / templates / static 分层，保证后续可以平滑补充 `/api/...` 并逐步前后端分离。

**Tech Stack:** Python, FastAPI, Jinja2, SQLAlchemy, Alembic, PostgreSQL, passlib/bcrypt, python-multipart, pytest

---

## 0. 实施前约束

- 遵循 DRY / YAGNI，只实现首版必须功能。
- 采用 TDD：先写失败测试，再写最小实现，再验证通过。
- 当前用户全局偏好禁止非查询类 git 操作，因此本计划**不包含实际 git add / commit / push 执行**；若后续用户明确解除限制，再补充提交步骤。
- 当前仓库几乎为空，以下文件大多为新建文件；若实际执行时已有同名文件，先读现状再调整。

## 1. 目标目录结构

```text
app/
  main.py
  core/
    config.py
    db.py
    security.py
    deps.py
  models/
    __init__.py
    user.py
    category.py
    tag.py
    post.py
  schemas/
    auth.py
    post.py
  services/
    auth_service.py
    post_service.py
    taxonomy_service.py
  routes/
    public.py
    admin_auth.py
    admin_posts.py
  templates/
    base.html
    public/
      index.html
      post_detail.html
      category_detail.html
      tag_detail.html
    admin/
      login.html
      post_list.html
      post_form.html
  static/
    css/style.css
    css/admin.css
migrations/
tests/
  conftest.py
  test_public_pages.py
  test_admin_auth.py
  test_admin_posts.py
requirements.txt
.env.example
alembic.ini
```

---

### Task 1: 初始化项目依赖与应用入口

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `app/main.py`
- Create: `app/core/config.py`
- Create: `app/core/db.py`
- Create: `app/models/__init__.py`
- Test: `tests/conftest.py`

**Step 1: 写失败测试，验证应用可创建**

```python
from fastapi.testclient import TestClient
from app.main import app


def test_health_route_exists():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/conftest.py -v`
Expected: FAIL，提示 `ModuleNotFoundError: No module named 'app'` 或 `/health` 不存在。

**Step 3: 写最小实现**

`requirements.txt` 至少包含：

```text
fastapi
uvicorn[standard]
jinja2
sqlalchemy
psycopg[binary]
alembic
passlib[bcrypt]
python-multipart
pytest
httpx
```

`app/core/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "myblog"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/myblog"
    secret_key: str = "change-me"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
```

`app/main.py`

```python
from fastapi import FastAPI

app = FastAPI(title="myblog")


@app.get("/health")
def health():
    return {"status": "ok"}
```

**Step 4: 运行测试确认通过**

Run: `pytest tests/conftest.py -v`
Expected: PASS

**Step 5: 安装依赖并人工验证启动**

Run: `uvicorn app.main:app --reload`
Expected: 访问 `/health` 返回 `{"status":"ok"}`

---

### Task 2: 建立数据库模型与基础映射

**Files:**
- Modify/Create: `app/core/db.py`
- Create: `app/models/user.py`
- Create: `app/models/category.py`
- Create: `app/models/tag.py`
- Create: `app/models/post.py`
- Modify: `app/models/__init__.py`
- Test: `tests/conftest.py`

**Step 1: 写失败测试，验证模型可建表与关系存在**

```python
from app.models import User, Category, Tag, Post


def test_models_have_expected_columns():
    assert User.__tablename__ == "users"
    assert Category.__tablename__ == "categories"
    assert Tag.__tablename__ == "tags"
    assert Post.__tablename__ == "posts"
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/conftest.py::test_models_have_expected_columns -v`
Expected: FAIL，提示模型未定义。

**Step 3: 写最小实现**

`app/core/db.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
```

`app/models/user.py`

```python
from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

`app/models/category.py`

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)

    posts = relationship("Post", back_populates="category")
```

`app/models/tag.py`

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)

    posts = relationship("Post", secondary="post_tags", back_populates="tags")
```

`app/models/post.py`

```python
from sqlalchemy import DateTime, ForeignKey, String, Table, Text, func, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True)
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    category = relationship("Category", back_populates="posts")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")
```

`app/models/__init__.py`

```python
from app.models.user import User
from app.models.category import Category
from app.models.tag import Tag
from app.models.post import Post, post_tags
```

**Step 4: 运行测试确认通过**

Run: `pytest tests/conftest.py::test_models_have_expected_columns -v`
Expected: PASS

**Step 5: 本地建表 smoke test**

Run: `python -c "from app.core.db import Base, engine; import app.models; Base.metadata.create_all(engine)"`
Expected: 表成功创建，无异常。

---

### Task 3: 添加 slug 生成逻辑与基础 service

**Files:**
- Create: `app/services/taxonomy_service.py`
- Create: `app/services/post_service.py`
- Test: `tests/test_admin_posts.py`

**Step 1: 写失败测试，验证 slug 生成规则**

```python
from app.services.post_service import slugify


def test_slugify_converts_title_to_url_slug():
    assert slugify("Hello World FastAPI") == "hello-world-fastapi"
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_admin_posts.py::test_slugify_converts_title_to_url_slug -v`
Expected: FAIL，提示 `slugify` 未定义。

**Step 3: 写最小实现**

`app/services/post_service.py`

```python
import re


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"[^a-z0-9\-]", "", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value
```

后续在同文件中继续补充：

```python
def ensure_unique_slug(base_slug: str, existing_slugs: set[str]) -> str:
    if base_slug not in existing_slugs:
        return base_slug

    index = 2
    while f"{base_slug}-{index}" in existing_slugs:
        index += 1
    return f"{base_slug}-{index}"
```

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_admin_posts.py::test_slugify_converts_title_to_url_slug -v`
Expected: PASS

**Step 5: 增补唯一 slug 测试**

```python
from app.services.post_service import ensure_unique_slug


def test_ensure_unique_slug_adds_suffix():
    assert ensure_unique_slug("hello-world", {"hello-world", "hello-world-2"}) == "hello-world-3"
```

Run: `pytest tests/test_admin_posts.py -v`
Expected: PASS

---

### Task 4: 配置 pytest 测试基座

**Files:**
- Create/Modify: `tests/conftest.py`
- Test: `tests/conftest.py`

**Step 1: 写失败测试，要求提供测试客户端和测试数据库 session**

```python
def test_client_fixture_smoke(client):
    response = client.get("/health")
    assert response.status_code == 200
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/conftest.py::test_client_fixture_smoke -v`
Expected: FAIL，提示 `fixture 'client' not found`。

**Step 3: 写最小实现**

`tests/conftest.py` 内容应包括：

```python
import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app
from app.core.db import Base


@pytest.fixture(scope="session")
def engine():
    engine = create_engine("sqlite:///./test.db", future=True)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture()
def client(engine):
    with TestClient(app) as test_client:
        yield test_client
```
```

执行时可根据最终依赖注入方式调整，但必须提供：
- 可复用测试 client
- 可隔离测试数据库
- 可在每个测试前后清理状态

**Step 4: 运行测试确认通过**

Run: `pytest tests/conftest.py -v`
Expected: PASS

**Step 5: 清理与改进**

- 若测试状态污染，改为每个测试事务回滚
- 若 SQLite 与 PostgreSQL 差异影响功能测试，保留 SQLite 做单元测试，后续再补 PostgreSQL 集成测试

---

### Task 5: 实现密码哈希与 session 鉴权基础设施

**Files:**
- Create: `app/core/security.py`
- Create: `app/core/deps.py`
- Create: `app/schemas/auth.py`
- Create: `app/services/auth_service.py`
- Test: `tests/test_admin_auth.py`

**Step 1: 写失败测试，验证密码哈希与校验**

```python
from app.core.security import hash_password, verify_password


def test_password_hash_and_verify():
    password = "secret123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_admin_auth.py::test_password_hash_and_verify -v`
Expected: FAIL

**Step 3: 写最小实现**

`app/core/security.py`

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)
```

`app/services/auth_service.py`

```python
from app.core.security import verify_password


def authenticate_user(user, password: str) -> bool:
    if not user or not user.is_active:
        return False
    return verify_password(password, user.password_hash)
```

`app/core/deps.py` 至少定义后台鉴权依赖接口。

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_admin_auth.py::test_password_hash_and_verify -v`
Expected: PASS

**Step 5: 增补 session 测试占位**

写一个失败测试，后续登录路由实现后填平：

```python
def test_admin_login_sets_session(client):
    response = client.post("/admin/login", data={"username": "admin", "password": "secret123"})
    assert response.status_code in (200, 302)
```
```

---

### Task 6: 实现管理员登录页与登录/登出路由

**Files:**
- Create: `app/routes/admin_auth.py`
- Create: `app/templates/admin/login.html`
- Modify: `app/main.py`
- Test: `tests/test_admin_auth.py`

**Step 1: 写失败测试，验证登录页可访问**

```python
def test_admin_login_page_renders(client):
    response = client.get("/admin/login")
    assert response.status_code == 200
    assert "登录" in response.text
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_admin_auth.py::test_admin_login_page_renders -v`
Expected: FAIL

**Step 3: 写最小实现**

`app/routes/admin_auth.py`

```python
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/admin", tags=["admin-auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})
```

`app/templates/admin/login.html`

```html
<!doctype html>
<html lang="zh-CN">
  <body>
    <h1>登录</h1>
    <form method="post">
      <input name="username" />
      <input name="password" type="password" />
      <button type="submit">登录</button>
    </form>
  </body>
</html>
```

`app/main.py` 注册路由。

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_admin_auth.py::test_admin_login_page_renders -v`
Expected: PASS

**Step 5: 实现 POST 登录与 GET 登出**

最小要求：
- 验证用户名密码
- 登录成功后写入 session
- 跳转到 `/admin/posts`
- 登出后清 session 并跳转 `/admin/login`

完成后补充测试：

```python
def test_admin_logout_clears_session(client):
    response = client.get("/admin/logout", follow_redirects=False)
    assert response.status_code == 302
```

---

### Task 7: 初始化模板基座与公共样式

**Files:**
- Create: `app/templates/base.html`
- Create: `app/static/css/style.css`
- Create: `app/static/css/admin.css`
- Modify: `app/main.py`
- Test: `tests/test_public_pages.py`

**Step 1: 写失败测试，验证首页模板可返回 HTML**

```python
def test_homepage_returns_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_public_pages.py::test_homepage_returns_html -v`
Expected: FAIL

**Step 3: 写最小实现**

- 在 `app/main.py` 挂载 `/static`
- 创建 `base.html`，提供站点标题、导航、样式链接
- 后续所有前后台模板都继承基础模板或保持统一结构

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_public_pages.py::test_homepage_returns_html -v`
Expected: PASS

**Step 5: 人工检查**

Run: `uvicorn app.main:app --reload`
Expected: 首页可渲染，无模板错误，CSS 可加载。

---

### Task 8: 实现前台首页文章列表页

**Files:**
- Create: `app/routes/public.py`
- Create: `app/templates/public/index.html`
- Modify: `app/services/post_service.py`
- Modify: `app/main.py`
- Test: `tests/test_public_pages.py`

**Step 1: 写失败测试，验证首页展示文章标题**

```python
def test_homepage_lists_posts(client, seeded_post):
    response = client.get("/")
    assert response.status_code == 200
    assert "My First Post" in response.text
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_public_pages.py::test_homepage_lists_posts -v`
Expected: FAIL

**Step 3: 写最小实现**

- `app/routes/public.py` 提供 `/`
- `app/services/post_service.py` 增加 `list_published_posts(session)`
- `index.html` 循环渲染文章标题、摘要、分类、标签入口

示例最小 service：

```python
from sqlalchemy import select
from app.models import Post


def list_published_posts(session):
    stmt = select(Post).order_by(Post.published_at.desc())
    return session.execute(stmt).scalars().all()
```

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_public_pages.py::test_homepage_lists_posts -v`
Expected: PASS

**Step 5: 增补空列表测试**

```python
def test_homepage_handles_empty_posts(client):
    response = client.get("/")
    assert "暂无文章" in response.text
```

---

### Task 9: 实现文章详情页

**Files:**
- Create: `app/templates/public/post_detail.html`
- Modify: `app/routes/public.py`
- Modify: `app/services/post_service.py`
- Test: `tests/test_public_pages.py`

**Step 1: 写失败测试，验证通过 slug 打开文章详情**

```python
def test_post_detail_uses_slug_route(client, seeded_post):
    response = client.get("/posts/my-first-post")
    assert response.status_code == 200
    assert "My First Post" in response.text
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_public_pages.py::test_post_detail_uses_slug_route -v`
Expected: FAIL

**Step 3: 写最小实现**

- 增加 `/posts/{slug}` 路由
- service 增加 `get_post_by_slug(session, slug)`
- 模板渲染标题、发布时间、正文、分类、标签
- slug 不存在时返回 404

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_public_pages.py::test_post_detail_uses_slug_route -v`
Expected: PASS

**Step 5: 增补 404 测试**

```python
def test_post_detail_returns_404_for_missing_slug(client):
    response = client.get("/posts/not-found")
    assert response.status_code == 404
```

---

### Task 10: 实现分类页与标签页

**Files:**
- Create: `app/templates/public/category_detail.html`
- Create: `app/templates/public/tag_detail.html`
- Modify: `app/routes/public.py`
- Modify: `app/services/taxonomy_service.py`
- Test: `tests/test_public_pages.py`

**Step 1: 写失败测试，验证分类页按 slug 展示文章**

```python
def test_category_page_lists_posts(client, seeded_post):
    response = client.get("/categories/python")
    assert response.status_code == 200
    assert "My First Post" in response.text
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_public_pages.py::test_category_page_lists_posts -v`
Expected: FAIL

**Step 3: 写最小实现**

- 增加 `/categories/{slug}` 与 `/tags/{slug}`
- taxonomy service 提供按 slug 查询分类/标签及其文章能力
- 模板展示当前分类/标签名称与文章列表

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_public_pages.py::test_category_page_lists_posts -v`
Expected: PASS

**Step 5: 增补标签测试**

```python
def test_tag_page_lists_posts(client, seeded_post):
    response = client.get("/tags/fastapi")
    assert response.status_code == 200
    assert "My First Post" in response.text
```

Run: `pytest tests/test_public_pages.py -v`
Expected: PASS

---

### Task 11: 定义文章表单 schema 与后台创建文章逻辑

**Files:**
- Create: `app/schemas/post.py`
- Modify: `app/services/post_service.py`
- Test: `tests/test_admin_posts.py`

**Step 1: 写失败测试，验证文章创建时自动生成 slug**

```python
from app.schemas.post import PostCreate
from app.services.post_service import build_post


def test_build_post_generates_slug():
    data = PostCreate(title="My First Post", summary="Intro", content="Hello", category_id=1, tag_ids=[])
    post = build_post(data, existing_slugs=set())
    assert post.slug == "my-first-post"
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_admin_posts.py::test_build_post_generates_slug -v`
Expected: FAIL

**Step 3: 写最小实现**

`app/schemas/post.py`

```python
from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    summary: str | None = None
    content: str
    category_id: int
    tag_ids: list[int] = []
```

`app/services/post_service.py` 增加：

```python
from app.models import Post
from app.schemas.post import PostCreate


def build_post(data: PostCreate, existing_slugs: set[str]) -> Post:
    slug = ensure_unique_slug(slugify(data.title), existing_slugs)
    return Post(
        title=data.title,
        slug=slug,
        summary=data.summary,
        content=data.content,
        category_id=data.category_id,
    )
```

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_admin_posts.py::test_build_post_generates_slug -v`
Expected: PASS

**Step 5: 增补更新文章 slug 策略测试**

先明确策略：
- 首版编辑文章时，默认**不自动改 slug**，防止链接变化。

测试示例：

```python
def test_edit_post_keeps_existing_slug():
    ...
```

---

### Task 12: 实现后台文章列表页

**Files:**
- Create: `app/routes/admin_posts.py`
- Create: `app/templates/admin/post_list.html`
- Modify: `app/main.py`
- Test: `tests/test_admin_posts.py`

**Step 1: 写失败测试，验证登录后可访问后台文章列表**

```python
def test_admin_post_list_requires_login(client):
    response = client.get("/admin/posts")
    assert response.status_code in (302, 303)
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_admin_posts.py::test_admin_post_list_requires_login -v`
Expected: FAIL

**Step 3: 写最小实现**

- `app/routes/admin_posts.py` 添加 `/admin/posts`
- 未登录时重定向 `/admin/login`
- 已登录时渲染文章列表模板

模板最小展示：
- 标题
- slug
- 分类
- 发布时间
- “新建文章”入口
- “编辑”入口

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_admin_posts.py::test_admin_post_list_requires_login -v`
Expected: PASS

**Step 5: 增补已登录场景测试**

```python
def test_admin_post_list_renders_after_login(client, logged_in_admin):
    response = client.get("/admin/posts")
    assert response.status_code == 200
    assert "文章管理" in response.text
```

---

### Task 13: 实现后台新建文章页与提交逻辑

**Files:**
- Create: `app/templates/admin/post_form.html`
- Modify: `app/routes/admin_posts.py`
- Modify: `app/services/post_service.py`
- Test: `tests/test_admin_posts.py`

**Step 1: 写失败测试，验证后台可创建文章**

```python
def test_admin_can_create_post(client, logged_in_admin, seeded_category, seeded_tags):
    response = client.post(
        "/admin/posts/new",
        data={
            "title": "My First Post",
            "summary": "Intro",
            "content": "Hello World",
            "category_id": seeded_category.id,
            "tag_ids": [tag.id for tag in seeded_tags],
        },
        follow_redirects=False,
    )
    assert response.status_code in (302, 303)
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_admin_posts.py::test_admin_can_create_post -v`
Expected: FAIL

**Step 3: 写最小实现**

- GET `/admin/posts/new` 返回表单页
- POST `/admin/posts/new`：
  - 读取表单
  - 校验必要字段
  - 查询现有 slug 集合
  - 创建文章
  - 关联标签
  - 写入数据库
  - 跳转 `/admin/posts`

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_admin_posts.py::test_admin_can_create_post -v`
Expected: PASS

**Step 5: 增补创建后前台可见测试**

```python
def test_created_post_visible_on_homepage(client, logged_in_admin, seeded_category):
    ...
```

---

### Task 14: 实现后台编辑文章页与提交逻辑

**Files:**
- Modify: `app/routes/admin_posts.py`
- Modify: `app/services/post_service.py`
- Modify: `app/templates/admin/post_form.html`
- Test: `tests/test_admin_posts.py`

**Step 1: 写失败测试，验证后台可编辑文章**

```python
def test_admin_can_edit_post(client, logged_in_admin, seeded_post):
    response = client.post(
        f"/admin/posts/{seeded_post.id}/edit",
        data={
            "title": "Updated Title",
            "summary": seeded_post.summary,
            "content": "Updated content",
            "category_id": seeded_post.category_id,
            "tag_ids": [],
        },
        follow_redirects=False,
    )
    assert response.status_code in (302, 303)
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_admin_posts.py::test_admin_can_edit_post -v`
Expected: FAIL

**Step 3: 写最小实现**

- GET `/admin/posts/{id}/edit` 回显表单
- POST `/admin/posts/{id}/edit` 更新标题、摘要、正文、分类、标签
- 默认保持原 slug 不变
- 提交后跳回 `/admin/posts`

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_admin_posts.py::test_admin_can_edit_post -v`
Expected: PASS

**Step 5: 增补 slug 保持不变测试**

```python
def test_edit_post_keeps_slug(client, logged_in_admin, seeded_post):
    original_slug = seeded_post.slug
    ...
    assert refreshed_post.slug == original_slug
```

---

### Task 15: 增加初始化管理员脚本或启动种子逻辑

**Files:**
- Create: `scripts/create_admin.py`
- Modify: `app/services/auth_service.py`
- Test: `tests/test_admin_auth.py`

**Step 1: 写失败测试，验证管理员创建逻辑可复用**

```python
from app.services.auth_service import build_admin_user


def test_build_admin_user_hashes_password():
    user = build_admin_user("admin", "secret123")
    assert user.username == "admin"
    assert user.password_hash != "secret123"
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_admin_auth.py::test_build_admin_user_hashes_password -v`
Expected: FAIL

**Step 3: 写最小实现**

- 在 `auth_service.py` 增加 `build_admin_user(username, password)`
- 新建 `scripts/create_admin.py`，支持命令行创建首个管理员

示例入口：

```python
from app.services.auth_service import build_admin_user

if __name__ == "__main__":
    ...
```

**Step 4: 运行测试确认通过**

Run: `pytest tests/test_admin_auth.py::test_build_admin_user_hashes_password -v`
Expected: PASS

**Step 5: 人工验证脚本**

Run: `python scripts/create_admin.py --username admin --password secret123`
Expected: 数据库生成管理员账户。

---

### Task 16: 引入 Alembic 并固化首版迁移

**Files:**
- Create: `alembic.ini`
- Create: `migrations/env.py`
- Create: `migrations/versions/<timestamp>_init_blog_tables.py`
- Modify: `app/core/db.py`
- Test: `tests/conftest.py`

**Step 1: 写失败测试，验证元数据可被迁移系统加载**

```python
from app.core.db import Base


def test_base_metadata_contains_blog_tables():
    table_names = set(Base.metadata.tables.keys())
    assert {"users", "categories", "tags", "posts", "post_tags"}.issubset(table_names)
```

**Step 2: 运行测试确认失败**

Run: `pytest tests/conftest.py::test_base_metadata_contains_blog_tables -v`
Expected: FAIL（若模型导入未汇总完全）。

**Step 3: 写最小实现**

- 初始化 Alembic
- `migrations/env.py` 指向 `Base.metadata`
- 生成首版迁移，包含：
  - users
  - categories
  - tags
  - posts
  - post_tags

**Step 4: 运行测试确认通过**

Run: `pytest tests/conftest.py::test_base_metadata_contains_blog_tables -v`
Expected: PASS

**Step 5: 人工验证迁移**

Run: `alembic upgrade head`
Expected: PostgreSQL 中所有首版表创建成功。

---

### Task 17: 完整回归测试与手工验收

**Files:**
- Test: `tests/test_public_pages.py`
- Test: `tests/test_admin_auth.py`
- Test: `tests/test_admin_posts.py`

**Step 1: 跑单元与路由测试**

Run: `pytest -v`
Expected: 全部 PASS

**Step 2: 手工启动应用**

Run: `uvicorn app.main:app --reload`
Expected: 应用成功启动，无导入错误。

**Step 3: 手工验收前台**

检查：
- `/` 首页文章列表正常
- `/posts/{slug}` 详情页正常
- `/categories/{slug}` 分类页正常
- `/tags/{slug}` 标签页正常

**Step 4: 手工验收后台**

检查：
- `/admin/login` 可登录
- `/admin/posts` 可查看文章列表
- `/admin/posts/new` 可创建文章
- `/admin/posts/{id}/edit` 可编辑文章

**Step 5: 记录验证结论**

将以下结果记录到当日优化日志：
- 需求/优化：博客 MVP 初始化
- 目的：搭建首版可上线闭环
- 模块：认证、文章管理、前台展示、数据库迁移
- 验证标准：上述页面与 CRUD 验证通过

建议命令：

Run: `python scripts/log_change.py --type "博客 MVP 初始化" --purpose "搭建首版可上线闭环" --modules "认证,文章管理,前台展示,数据库迁移" --verification "首页/详情/分类/标签/后台登录/创建/编辑验证通过"`
Expected: `project_logs/optimization/YYYY-MM-DD.md` 写入成功

---

## 实施顺序建议

按以下顺序执行，能减少返工：

1. Task 1-4：先把应用骨架、模型、slug、测试基座搭起来
2. Task 5-6：完成管理员认证闭环
3. Task 7-10：完成前台展示闭环
4. Task 11-14：完成后台文章管理闭环
5. Task 15-16：补管理员初始化与数据库迁移
6. Task 17：统一回归与日志记录

## 明确暂不实现

以下内容全部不进入本轮开发：

- 评论系统
- 搜索
- RSS
- SEO 精细化字段
- 草稿 / 定时发布
- 图片上传 / 附件管理
- 访问统计
- React / Vue 前后端分离
- JWT API 鉴权

## 后续演进接口

后续前后端分离时，优先沿以下方向扩展：

- 保留现有 `services/` 作为业务层
- 在 `routes/` 下新增 `api/` 模块输出 JSON
- 后台可先分离，再视需要分离前台
- 如需草稿功能，再给 `Post` 增加 `status`
- 如需 SEO，再补充 `meta_title`、`meta_description`

