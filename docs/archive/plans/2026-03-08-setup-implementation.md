# Setup Wizard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a first-run web setup flow for this personal blog so uninitialized installs redirect to `/setup`, create the database-backed site title and single admin account, then auto-login into the admin area.

**Architecture:** Add a new `SiteSettings` model plus migration, then introduce a dedicated `setup_service` and `setup` router to own initialization checks and the one-time install flow. Existing public and admin routes will call a small initialization guard so `/` and admin pages redirect to `/setup` before installation, while `/setup` becomes unavailable after installation.

**Tech Stack:** FastAPI, Jinja2 templates, SQLAlchemy ORM, Alembic, pytest, TestClient, SessionMiddleware

---

## Implementation Notes

- Follow @superpowers:test-driven-development for every behavior change: write the failing test first, run it and see it fail, then write the minimal implementation.
- Do **not** introduce multi-user or role-management features. This remains a single-admin personal blog.
- Do **not** add extra site settings beyond `blog_title`.
- Production initialization path should call Alembic upgrade logic; tests may continue to use the existing lightweight metadata-driven setup in `tests/conftest.py`.
- User preference forbids git write operations in this repository, so commit steps are intentionally omitted from this plan.

---

### Task 1: Add the site settings model and metadata coverage

**Files:**
- Modify: `app/models/__init__.py`
- Create: `app/models/site_settings.py`
- Modify: `tests/conftest.py`
- Test: `tests/test_setup_service.py`

**Step 1: Write the failing test**

Create `tests/test_setup_service.py` with a metadata-focused test that proves the new table is registered:

```python
from app.core.db import Base


def test_base_metadata_contains_site_settings_table() -> None:
    assert "site_settings" in Base.metadata.tables
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_setup_service.py::test_base_metadata_contains_site_settings_table -v`
Expected: FAIL because the `site_settings` table does not exist yet.

**Step 3: Write minimal implementation**

Create `app/models/site_settings.py` with a minimal SQLAlchemy model consistent with the existing model style:

```python
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class SiteSettings(Base):
    __tablename__ = "site_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    blog_title: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
```

Update `app/models/__init__.py` to import and export `SiteSettings` alongside the existing models.

Update the metadata assertion in `tests/conftest.py:22-24` so the expected table set includes `site_settings`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_setup_service.py::test_base_metadata_contains_site_settings_table tests/conftest.py::test_base_metadata_contains_blog_tables -v`
Expected: PASS.

---

### Task 2: Add the Alembic migration for site settings

**Files:**
- Create: `migrations/versions/20260308_add_site_settings.py`
- Test: `tests/test_setup_service.py`

**Step 1: Write the failing test**

Add a migration-presence test in `tests/test_setup_service.py`:

```python
from pathlib import Path


def test_site_settings_migration_file_exists() -> None:
    migration = Path("migrations/versions/20260308_add_site_settings.py")
    assert migration.exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_setup_service.py::test_site_settings_migration_file_exists -v`
Expected: FAIL because the new migration file does not exist yet.

**Step 3: Write minimal implementation**

Create `migrations/versions/20260308_add_site_settings.py`:

```python
from alembic import op
import sqlalchemy as sa

revision = "20260308_add_site_settings"
down_revision = "20260308_init_blog_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "site_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("blog_title", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("site_settings")
```

Keep the migration focused: only add `site_settings`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_setup_service.py::test_site_settings_migration_file_exists -v`
Expected: PASS.

---

### Task 3: Implement initialization state checks and setup domain service

**Files:**
- Create: `app/services/setup_service.py`
- Modify: `app/services/auth_service.py`
- Modify: `tests/test_setup_service.py`

**Step 1: Write the failing tests**

Add service tests to `tests/test_setup_service.py`:

```python
from app.models import SiteSettings
from app.services.auth_service import build_admin_user
from app.services.setup_service import is_initialized


def test_is_initialized_returns_false_when_database_has_no_setup_data(db_session):
    assert is_initialized(db_session) is False


def test_is_initialized_returns_false_with_only_admin(db_session):
    db_session.add(build_admin_user("admin", "secret123"))
    db_session.commit()
    assert is_initialized(db_session) is False


def test_is_initialized_returns_false_with_only_site_settings(db_session):
    db_session.add(SiteSettings(blog_title="My Blog"))
    db_session.commit()
    assert is_initialized(db_session) is False


def test_is_initialized_returns_true_with_site_settings_and_admin(db_session):
    db_session.add(SiteSettings(blog_title="My Blog"))
    db_session.add(build_admin_user("admin", "secret123"))
    db_session.commit()
    assert is_initialized(db_session) is True
```

Also add an initialization test that defines the target API:

```python
from app.services.setup_service import initialize_site, SetupAlreadyInitializedError


def test_initialize_site_creates_site_settings_and_admin(db_session):
    user = initialize_site(
        db=db_session,
        blog_title="My Blog",
        username="admin",
        password="secret123",
    )

    db_session.refresh(user)
    settings = db_session.query(SiteSettings).one()
    assert settings.blog_title == "My Blog"
    assert user.username == "admin"
    assert user.password_hash != "secret123"
```

Add a repeat-install guard test:

```python
import pytest


def test_initialize_site_rejects_repeat_install(db_session):
    initialize_site(db=db_session, blog_title="My Blog", username="admin", password="secret123")

    with pytest.raises(SetupAlreadyInitializedError):
        initialize_site(db=db_session, blog_title="Other Blog", username="root", password="otherpass")
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_setup_service.py -v`
Expected: FAIL because `setup_service` and the new APIs do not exist yet.

**Step 3: Write minimal implementation**

Create `app/services/setup_service.py` with these pieces:

```python
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.models import SiteSettings, User
from app.services.auth_service import build_admin_user


class SetupAlreadyInitializedError(Exception):
    pass


REQUIRED_TABLES = {"users", "site_settings"}


def _has_required_tables(db: Session) -> bool:
    inspector = inspect(db.bind)
    return REQUIRED_TABLES.issubset(set(inspector.get_table_names()))


def is_initialized(db: Session) -> bool:
    if not _has_required_tables(db):
        return False

    has_site_settings = db.execute(select(SiteSettings.id).limit(1)).first() is not None
    has_admin = db.execute(select(User.id).limit(1)).first() is not None
    return has_site_settings and has_admin


def get_site_settings(db: Session) -> SiteSettings | None:
    if not _has_required_tables(db):
        return None
    return db.execute(select(SiteSettings)).scalar_one_or_none()


def initialize_site(db: Session, blog_title: str, username: str, password: str) -> User:
    if is_initialized(db):
        raise SetupAlreadyInitializedError()

    site_settings = SiteSettings(blog_title=blog_title)
    user = build_admin_user(username, password)
    db.add(site_settings)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

If needed, add a small helper in `app/services/auth_service.py` to query whether any users exist, but do not add broader auth abstractions.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_setup_service.py -v`
Expected: PASS.

---

### Task 4: Add Alembic upgrade helper for the setup flow

**Files:**
- Create: `app/services/migration_service.py`
- Modify: `tests/test_setup_service.py`

**Step 1: Write the failing test**

Add a patch-based contract test in `tests/test_setup_service.py`:

```python
from unittest.mock import patch

from app.services.migration_service import upgrade_database


def test_upgrade_database_calls_alembic_upgrade() -> None:
    with patch("app.services.migration_service.command.upgrade") as mock_upgrade:
        upgrade_database()

    mock_upgrade.assert_called_once()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_setup_service.py::test_upgrade_database_calls_alembic_upgrade -v`
Expected: FAIL because `migration_service` does not exist yet.

**Step 3: Write minimal implementation**

Create `app/services/migration_service.py`:

```python
from pathlib import Path

from alembic import command
from alembic.config import Config


def upgrade_database() -> None:
    config = Config(str(Path("alembic.ini")))
    command.upgrade(config, "head")
```

Keep it minimal. The setup route will call this helper before initialization writes.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_setup_service.py::test_upgrade_database_calls_alembic_upgrade -v`
Expected: PASS.

---

### Task 5: Add the setup page template and route skeleton

**Files:**
- Create: `app/routes/setup.py`
- Create: `app/templates/setup/setup.html`
- Modify: `app/main.py`
- Modify: `tests/test_public_pages.py`
- Modify: `tests/test_admin_auth.py`

**Step 1: Write the failing tests**

Add an uninitialized routing test to `tests/test_public_pages.py`:

```python
def test_home_redirects_to_setup_when_uninitialized(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/setup"
```

Add a setup page test to `tests/test_admin_auth.py`:

```python
def test_setup_page_is_available_when_uninitialized(client):
    response = client.get("/setup")
    assert response.status_code == 200
    assert "博客标题" in response.text
    assert "管理员用户名" in response.text
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_public_pages.py::test_home_redirects_to_setup_when_uninitialized tests/test_admin_auth.py::test_setup_page_is_available_when_uninitialized -v`
Expected: FAIL because `/setup` is not registered and `/` still renders the home page.

**Step 3: Write minimal implementation**

Create `app/routes/setup.py`:

```python
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.setup_service import is_initialized

router = APIRouter(tags=["setup"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/setup", response_class=HTMLResponse)
def setup_page(request: Request, db: Session = Depends(get_db)):
    if is_initialized(db):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(request, "setup/setup.html", {"error": None})
```

Create `app/templates/setup/setup.html` with a basic HTML form that posts to `/setup` and includes labels for `blog_title`, `username`, `password`, and `confirm_password`.

Register the router in `app/main.py` before public/admin routes that may redirect.

Temporarily update the public home route in `app/routes/public.py` so it redirects to `/setup` when `is_initialized(db)` is false.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_public_pages.py::test_home_redirects_to_setup_when_uninitialized tests/test_admin_auth.py::test_setup_page_is_available_when_uninitialized -v`
Expected: PASS.

---

### Task 6: Implement setup submission, validation, and auto-login

**Files:**
- Modify: `app/routes/setup.py`
- Modify: `app/services/setup_service.py`
- Modify: `tests/test_admin_auth.py`

**Step 1: Write the failing tests**

Add these route tests to `tests/test_admin_auth.py`:

```python
def test_setup_submission_initializes_site_and_redirects_to_admin_posts(client, db_session):
    response = client.post(
        "/setup",
        data={
            "blog_title": "我的博客",
            "username": "admin",
            "password": "secret123",
            "confirm_password": "secret123",
        },
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/admin/posts"
```

```python
def test_setup_submission_rejects_password_mismatch(client):
    response = client.post(
        "/setup",
        data={
            "blog_title": "我的博客",
            "username": "admin",
            "password": "secret123",
            "confirm_password": "wrong",
        },
    )

    assert response.status_code == 400
    assert "两次密码不一致" in response.text
```

```python
def test_setup_submission_redirects_home_when_already_initialized(client, db_session):
    from app.models import SiteSettings
    from app.services.auth_service import build_admin_user

    db_session.add(SiteSettings(blog_title="My Blog"))
    db_session.add(build_admin_user("admin", "secret123"))
    db_session.commit()

    response = client.post(
        "/setup",
        data={
            "blog_title": "Another Blog",
            "username": "root",
            "password": "secret123",
            "confirm_password": "secret123",
        },
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/"
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_admin_auth.py::test_setup_submission_initializes_site_and_redirects_to_admin_posts tests/test_admin_auth.py::test_setup_submission_rejects_password_mismatch tests/test_admin_auth.py::test_setup_submission_redirects_home_when_already_initialized -v`
Expected: FAIL because `POST /setup` is not implemented yet.

**Step 3: Write minimal implementation**

Add `POST /setup` to `app/routes/setup.py`:

```python
from fastapi import Form, status

from app.services.migration_service import upgrade_database
from app.services.setup_service import SetupAlreadyInitializedError, initialize_site


@router.post("/setup")
def setup_submit(
    request: Request,
    blog_title: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    if is_initialized(db):
        return RedirectResponse(url="/", status_code=302)

    if password != confirm_password:
        return templates.TemplateResponse(
            request,
            "setup/setup.html",
            {"error": "两次密码不一致"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    upgrade_database()

    try:
        user = initialize_site(db=db, blog_title=blog_title, username=username, password=password)
    except SetupAlreadyInitializedError:
        return RedirectResponse(url="/", status_code=302)

    request.session["user_id"] = user.id
    return RedirectResponse(url="/admin/posts", status_code=302)
```

If form re-rendering needs previous values, pass `form_data` to the template, but keep the change minimal.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_admin_auth.py::test_setup_submission_initializes_site_and_redirects_to_admin_posts tests/test_admin_auth.py::test_setup_submission_rejects_password_mismatch tests/test_admin_auth.py::test_setup_submission_redirects_home_when_already_initialized -v`
Expected: PASS.

---

### Task 7: Protect admin routes behind initialization guard

**Files:**
- Modify: `app/routes/admin_auth.py`
- Modify: `app/routes/admin_posts.py`
- Modify: `tests/test_admin_auth.py`
- Modify: `tests/test_admin_posts.py`

**Step 1: Write the failing tests**

Add to `tests/test_admin_auth.py`:

```python
def test_admin_login_redirects_to_setup_when_uninitialized(client):
    response = client.get("/admin/login", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/setup"
```

Add to `tests/test_admin_posts.py`:

```python
def test_admin_posts_redirects_to_setup_when_uninitialized(client):
    response = client.get("/admin/posts", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/setup"
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_admin_auth.py::test_admin_login_redirects_to_setup_when_uninitialized tests/test_admin_posts.py::test_admin_posts_redirects_to_setup_when_uninitialized -v`
Expected: FAIL because admin routes still use their previous behavior.

**Step 3: Write minimal implementation**

Use `is_initialized(db)` in the admin route entry points:

- In `app/routes/admin_auth.py:12-34`, inject `db: Session = Depends(get_db)` into `login_page` and redirect to `/setup` when uninitialized.
- In `app/routes/admin_auth.py:17-34`, short-circuit `POST /admin/login` to `/setup` when uninitialized.
- In `app/routes/admin_posts.py`, update `_require_login` (or add a small wrapper) so initialization is checked before ordinary session-login logic.

Prefer a tiny helper such as:

```python
def _require_initialized(db: Session) -> RedirectResponse | None:
    if not is_initialized(db):
        return RedirectResponse(url="/setup", status_code=302)
    return None
```

Do not add global middleware yet; keep the behavior explicit in route functions.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_admin_auth.py::test_admin_login_redirects_to_setup_when_uninitialized tests/test_admin_posts.py::test_admin_posts_redirects_to_setup_when_uninitialized -v`
Expected: PASS.

---

### Task 8: Disable setup after installation and display the blog title on the public home page

**Files:**
- Modify: `app/routes/public.py`
- Modify: `app/templates/base.html`
- Modify: `app/templates/public/index.html`
- Modify: `app/routes/setup.py`
- Modify: `tests/test_public_pages.py`
- Modify: `tests/test_admin_auth.py`

**Step 1: Write the failing tests**

Add a post-initialization test to `tests/test_admin_auth.py`:

```python
def test_setup_page_redirects_home_when_initialized(client, db_session):
    from app.models import SiteSettings
    from app.services.auth_service import build_admin_user

    db_session.add(SiteSettings(blog_title="我的博客"))
    db_session.add(build_admin_user("admin", "secret123"))
    db_session.commit()

    response = client.get("/setup", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/"
```

Add a public rendering test to `tests/test_public_pages.py`:

```python
def test_home_displays_database_blog_title_when_initialized(client, db_session):
    from app.models import SiteSettings
    from app.services.auth_service import build_admin_user

    db_session.add(SiteSettings(blog_title="我的博客"))
    db_session.add(build_admin_user("admin", "secret123"))
    db_session.commit()

    response = client.get("/")
    assert response.status_code == 200
    assert "我的博客" in response.text
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_admin_auth.py::test_setup_page_redirects_home_when_initialized tests/test_public_pages.py::test_home_displays_database_blog_title_when_initialized -v`
Expected: FAIL because the home page does not yet render the database-backed title.

**Step 3: Write minimal implementation**

In `app/routes/public.py`, when initialized:
- fetch the site settings via `get_site_settings(db)`
- pass `site_title` into the template context

In `app/templates/base.html`, replace any hardcoded title text with `{{ site_title or "myblog" }}` for the `<title>` and top-level heading if present.

In `app/templates/public/index.html`, ensure the page surfaces `site_title` somewhere visible so the test can assert on it.

Keep `/setup` redirect behavior from Task 5/6 unchanged when initialized.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_admin_auth.py::test_setup_page_redirects_home_when_initialized tests/test_public_pages.py::test_home_displays_database_blog_title_when_initialized -v`
Expected: PASS.

---

### Task 9: Run focused regression tests for the setup flow and existing auth/public behavior

**Files:**
- Modify if needed: `tests/test_setup_service.py`
- Modify if needed: `tests/test_admin_auth.py`
- Modify if needed: `tests/test_admin_posts.py`
- Modify if needed: `tests/test_public_pages.py`

**Step 1: Run the focused test suite**

Run:

```bash
pytest tests/test_setup_service.py tests/test_admin_auth.py tests/test_admin_posts.py tests/test_public_pages.py -v
```

Expected: PASS, with the new setup flow covered and no regressions in admin/public behavior.

**Step 2: Fix any failures minimally**

If any tests fail:
- add the smallest missing template context
- adjust redirects/status codes consistently
- keep changes local to setup/init behavior

**Step 3: Re-run the focused suite**

Run the same command again:

```bash
pytest tests/test_setup_service.py tests/test_admin_auth.py tests/test_admin_posts.py tests/test_public_pages.py -v
```

Expected: PASS.

---

### Task 10: Run full project regression verification

**Files:**
- No intended code changes; only touch files if failures reveal required setup-related regressions.

**Step 1: Run the full test suite**

Run:

```bash
pytest -v
```

Expected: PASS for the whole project.

**Step 2: If failures appear, fix only setup-caused regressions**

Stay within scope:
- metadata expectations
- auth redirects
- template context expectations
- home-page rendering assumptions

Do not refactor unrelated modules.

**Step 3: Re-run full verification**

Run:

```bash
pytest -v
```

Expected: PASS.

---

## Final Verification Checklist

Before declaring the work complete, verify all of the following with fresh evidence:

- `/` redirects to `/setup` when uninitialized
- `/setup` renders when uninitialized
- `POST /setup` creates `site_settings` and one admin user
- `POST /setup` rejects password mismatch
- setup success writes session and redirects to `/admin/posts`
- `/setup` redirects to `/` after initialization
- `/admin/login` and `/admin/posts` redirect to `/setup` when uninitialized
- the public home page displays the database-backed blog title after initialization
- full `pytest -v` passes
