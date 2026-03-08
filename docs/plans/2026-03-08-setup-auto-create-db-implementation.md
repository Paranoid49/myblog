# Setup Auto-Create PostgreSQL Database Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the `/setup` flow automatically create the target PostgreSQL database when `DATABASE_URL` points to a database that does not exist yet, then continue with migration, initialization, and auto-login.

**Architecture:** Add a small `database_bootstrap_service` dedicated to setup-time PostgreSQL database existence checks and creation. Refactor `app/routes/setup.py` so it no longer depends on a target-database `Session` before bootstrap completes; instead it will bootstrap first, run Alembic migrations second, then manually create a session and call the existing setup service.

**Tech Stack:** FastAPI, Jinja2 templates, SQLAlchemy, psycopg/PostgreSQL, Alembic, pytest, TestClient, unittest.mock

---

## Implementation Notes

- Follow @superpowers:test-driven-development for every behavior change: write the failing test first, run it and watch it fail, then write the smallest implementation that passes.
- This feature supports **PostgreSQL only**. Do not add MySQL, SQLite, or cross-database abstractions.
- Keep bootstrap responsibilities separate from migration responsibilities and setup-data responsibilities.
- User preference forbids git write operations in this repository, so commit steps are intentionally omitted from this plan.
- Reuse current setup semantics: the system is initialized only when both `site_settings` and an admin `User` exist.

---

### Task 1: Add PostgreSQL bootstrap service contract tests

**Files:**
- Create: `tests/test_database_bootstrap_service.py`
- Read for reference: `app/core/config.py`
- Read for reference: `app/core/db.py`

**Step 1: Write the failing tests**

Create `tests/test_database_bootstrap_service.py` with explicit API-shaping tests:

```python
import pytest

from app.services.database_bootstrap_service import (
    DatabaseBootstrapError,
    UnsupportedDatabaseBootstrapError,
    build_maintenance_database_url,
)


def test_build_maintenance_database_url_replaces_target_database_name() -> None:
    url = "postgresql+psycopg://postgres:123456@localhost:5432/myblog"

    result = build_maintenance_database_url(url)

    assert result == "postgresql+psycopg://postgres:123456@localhost:5432/postgres"


def test_build_maintenance_database_url_rejects_non_postgresql_url() -> None:
    with pytest.raises(UnsupportedDatabaseBootstrapError):
        build_maintenance_database_url("sqlite:///./test.db")
```

Add two behavior tests using patching to define the service contract:

```python
from unittest.mock import MagicMock, patch

from app.services.database_bootstrap_service import ensure_database_exists


def test_ensure_database_exists_skips_create_when_database_already_exists() -> None:
    scalar_result = MagicMock(return_value=True)
    execute_result = MagicMock(scalar=scalar_result)
    connection = MagicMock()
    connection.execute.return_value = execute_result
    context_manager = MagicMock()
    context_manager.__enter__.return_value = connection
    engine = MagicMock()
    engine.begin.return_value = context_manager

    with patch("app.services.database_bootstrap_service.create_engine", return_value=engine):
        ensure_database_exists("postgresql+psycopg://postgres:123456@localhost:5432/myblog")

    connection.execute.assert_called_once()


def test_ensure_database_exists_creates_database_when_missing() -> None:
    scalar_result = MagicMock(return_value=False)
    execute_result = MagicMock(scalar=scalar_result)
    connection = MagicMock()
    connection.execute.side_effect = [execute_result, None]
    context_manager = MagicMock()
    context_manager.__enter__.return_value = connection
    engine = MagicMock()
    engine.begin.return_value = context_manager

    with patch("app.services.database_bootstrap_service.create_engine", return_value=engine):
        ensure_database_exists("postgresql+psycopg://postgres:123456@localhost:5432/myblog")

    assert connection.execute.call_count == 2
```

Add an error-wrapping test:

```python
def test_ensure_database_exists_wraps_create_failures() -> None:
    connection = MagicMock()
    connection.execute.side_effect = RuntimeError("permission denied")
    context_manager = MagicMock()
    context_manager.__enter__.return_value = connection
    engine = MagicMock()
    engine.begin.return_value = context_manager

    with patch("app.services.database_bootstrap_service.create_engine", return_value=engine):
        with pytest.raises(DatabaseBootstrapError):
            ensure_database_exists("postgresql+psycopg://postgres:123456@localhost:5432/myblog")
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_database_bootstrap_service.py -v`
Expected: FAIL because `app.services.database_bootstrap_service` does not exist yet.

**Step 3: Write minimal implementation**

Create `app/services/database_bootstrap_service.py` with this minimal structure:

```python
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


class DatabaseBootstrapError(Exception):
    pass


class UnsupportedDatabaseBootstrapError(DatabaseBootstrapError):
    pass


def build_maintenance_database_url(database_url: str) -> str:
    url = make_url(database_url)
    if not url.drivername.startswith("postgresql"):
        raise UnsupportedDatabaseBootstrapError()
    return str(url.set(database="postgres"))


def _get_target_database_name(database_url: str) -> str:
    url = make_url(database_url)
    if not url.database:
        raise DatabaseBootstrapError()
    return url.database


def ensure_database_exists(database_url: str) -> None:
    maintenance_url = build_maintenance_database_url(database_url)
    target_database = _get_target_database_name(database_url)
    engine = create_engine(maintenance_url, future=True, isolation_level="AUTOCOMMIT")

    try:
        with engine.begin() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
                {"database_name": target_database},
            ).scalar()
            if exists:
                return
            connection.execute(text(f'CREATE DATABASE "{target_database}"'))
    except UnsupportedDatabaseBootstrapError:
        raise
    except Exception as exc:
        raise DatabaseBootstrapError() from exc
    finally:
        engine.dispose()
```

Keep it focused. Do not add logging, retries, or reusable database frameworks.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_database_bootstrap_service.py -v`
Expected: PASS.

---

### Task 2: Add setup route tests for bootstrap-first behavior

**Files:**
- Modify: `tests/test_admin_auth.py`
- Read for reference: `app/routes/setup.py`
- Read for reference: `tests/conftest.py`

**Step 1: Write the failing tests**

Add a GET-path test that defines the new behavior without requiring a target database session:

```python
from unittest.mock import patch


def test_setup_page_is_available_when_target_database_does_not_exist(client) -> None:
    with patch("app.routes.setup.database_exists", return_value=False):
        response = client.get("/setup")

    assert response.status_code == 200
    assert "博客标题" in response.text
```

Add a POST-path orchestration test:

```python
def test_setup_submission_bootstraps_database_before_migration_and_initialization(client, db_session) -> None:
    with (
        patch("app.routes.setup.ensure_database_exists") as mock_bootstrap,
        patch("app.routes.setup.upgrade_database") as mock_upgrade,
        patch("app.routes.setup.create_session") as mock_create_session,
        patch("app.routes.setup.initialize_site") as mock_initialize,
    ):
        mock_create_session.return_value.__enter__.return_value = db_session
        mock_initialize.return_value.id = 1

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
    mock_bootstrap.assert_called_once()
    mock_upgrade.assert_called_once()
    mock_create_session.assert_called_once()
    mock_initialize.assert_called_once()
```

Add a bootstrap-failure test:

```python
from app.services.database_bootstrap_service import DatabaseBootstrapError


def test_setup_submission_shows_generic_error_when_bootstrap_fails(client) -> None:
    with patch("app.routes.setup.ensure_database_exists", side_effect=DatabaseBootstrapError()):
        response = client.post(
            "/setup",
            data={
                "blog_title": "我的博客",
                "username": "admin",
                "password": "secret123",
                "confirm_password": "secret123",
            },
        )

    assert response.status_code == 400
    assert "初始化失败，请检查数据库配置后重试" in response.text
```

Add a password-mismatch guard test to ensure bootstrap is not called:

```python
def test_setup_submission_does_not_bootstrap_when_password_mismatch(client) -> None:
    with patch("app.routes.setup.ensure_database_exists") as mock_bootstrap:
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
    mock_bootstrap.assert_not_called()
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_admin_auth.py::test_setup_page_is_available_when_target_database_does_not_exist tests/test_admin_auth.py::test_setup_submission_bootstraps_database_before_migration_and_initialization tests/test_admin_auth.py::test_setup_submission_shows_generic_error_when_bootstrap_fails tests/test_admin_auth.py::test_setup_submission_does_not_bootstrap_when_password_mismatch -v`
Expected: FAIL because the setup route does not expose these bootstrap-friendly seams yet.

**Step 3: Write minimal implementation scaffolding**

Refactor `app/routes/setup.py` to introduce small seams the tests can patch:

```python
from contextlib import contextmanager

from app.core.config import settings
from app.core.db import SessionLocal
from app.services.database_bootstrap_service import DatabaseBootstrapError, ensure_database_exists


@contextmanager
def create_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def database_exists() -> bool:
    try:
        ensure_database_exists(settings.database_url)
        return True
    except DatabaseBootstrapError:
        return False
```

Do **not** finalize behavior yet. Only add the pieces needed so the route can be refactored in the next task.

**Step 4: Run tests to verify partial progress**

Run: `pytest tests/test_admin_auth.py::test_setup_submission_does_not_bootstrap_when_password_mismatch -v`
Expected: This one may pass first after scaffolding; the others should still fail until route flow is fully updated.

---

### Task 3: Refactor setup GET/POST to avoid pre-bootstrap target-db dependency

**Files:**
- Modify: `app/routes/setup.py`
- Modify: `tests/test_admin_auth.py`
- Read for reference: `app/services/setup_service.py:20-45`
- Read for reference: `app/services/migration_service.py:1-9`

**Step 1: Write one more failing test for already-initialized GET behavior**

Add this regression-focused test to `tests/test_admin_auth.py` if it is not already in the right shape for the new route internals:

```python
def test_setup_page_redirects_home_when_initialized(client, db_session) -> None:
    from app.models import SiteSettings
    from app.services.auth_service import build_admin_user

    db_session.add(SiteSettings(blog_title="我的博客"))
    db_session.add(build_admin_user("admin", "secret123"))
    db_session.commit()

    with patch("app.routes.setup.database_exists", return_value=True):
        response = client.get("/setup", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/"
```

**Step 2: Run the focused tests to verify failure**

Run: `pytest tests/test_admin_auth.py::test_setup_page_is_available_when_target_database_does_not_exist tests/test_admin_auth.py::test_setup_page_redirects_home_when_initialized tests/test_admin_auth.py::test_setup_submission_bootstraps_database_before_migration_and_initialization tests/test_admin_auth.py::test_setup_submission_shows_generic_error_when_bootstrap_fails -v`
Expected: FAIL until GET and POST are fully refactored.

**Step 3: Write minimal implementation**

Update `app/routes/setup.py` so `GET /setup` and `POST /setup` no longer inject `db: Session = Depends(get_db)`.

Target shape:

```python
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.db import SessionLocal
from app.services.database_bootstrap_service import DatabaseBootstrapError, ensure_database_exists
from app.services.migration_service import upgrade_database
from app.services.setup_service import SetupAlreadyInitializedError, initialize_site, is_initialized

router = APIRouter(tags=["setup"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/setup", response_class=HTMLResponse)
def setup_page(request: Request):
    if not database_exists():
        return templates.TemplateResponse(request, "setup/setup.html", {"error": None})

    with create_session() as db:
        if is_initialized(db):
            return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse(request, "setup/setup.html", {"error": None})


@router.post("/setup")
def setup_submit(
    request: Request,
    blog_title: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    if password != confirm_password:
        return templates.TemplateResponse(
            request,
            "setup/setup.html",
            {"error": "两次密码不一致"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        ensure_database_exists(settings.database_url)
        upgrade_database()
        with create_session() as db:
            if is_initialized(db):
                return RedirectResponse(url="/", status_code=302)
            user = initialize_site(db=db, blog_title=blog_title, username=username, password=password)
    except SetupAlreadyInitializedError:
        return RedirectResponse(url="/", status_code=302)
    except DatabaseBootstrapError:
        return templates.TemplateResponse(
            request,
            "setup/setup.html",
            {"error": "初始化失败，请检查数据库配置后重试"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    request.session["user_id"] = user.id
    return RedirectResponse(url="/admin/posts", status_code=302)
```

Keep the error handling minimal and exactly scoped to setup.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_admin_auth.py -v`
Expected: PASS.

---

### Task 4: Tighten bootstrap service safety and SQL behavior

**Files:**
- Modify: `tests/test_database_bootstrap_service.py`
- Modify: `app/services/database_bootstrap_service.py`

**Step 1: Write the failing test for safe SQL construction**

Add a test proving the service quotes the database name through SQLAlchemy identifiers rather than raw string concatenation:

```python
from unittest.mock import MagicMock, patch


def test_ensure_database_exists_uses_identifier_preparer_for_create_database() -> None:
    scalar_result = MagicMock(return_value=False)
    execute_result = MagicMock(scalar=scalar_result)
    connection = MagicMock()
    connection.execute.side_effect = [execute_result, None]
    context_manager = MagicMock()
    context_manager.__enter__.return_value = connection
    engine = MagicMock()
    engine.begin.return_value = context_manager
    engine.dialect.identifier_preparer.quote.side_effect = lambda value: f'"{value}"'

    with patch("app.services.database_bootstrap_service.create_engine", return_value=engine):
        ensure_database_exists("postgresql+psycopg://postgres:123456@localhost:5432/myblog")

    engine.dialect.identifier_preparer.quote.assert_called_once_with("myblog")
```

**Step 2: Run the focused test to verify it fails**

Run: `pytest tests/test_database_bootstrap_service.py::test_ensure_database_exists_uses_identifier_preparer_for_create_database -v`
Expected: FAIL if the implementation still interpolates the database name directly.

**Step 3: Write minimal implementation**

Update the create path in `app/services/database_bootstrap_service.py`:

```python
quoted_database_name = engine.dialect.identifier_preparer.quote(target_database)
connection.execute(text(f"CREATE DATABASE {quoted_database_name}"))
```

Do not introduce helper classes or extra abstractions.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_database_bootstrap_service.py -v`
Expected: PASS.

---

### Task 5: Add route-level regression coverage for existing setup semantics

**Files:**
- Modify: `tests/test_admin_auth.py`
- Read for reference: `tests/test_public_pages.py`
- Read for reference: `tests/test_admin_posts.py`

**Step 1: Write the failing regression tests**

Ensure `tests/test_admin_auth.py` contains or adds these checks in bootstrap-compatible form:

```python
def test_setup_submission_redirects_home_when_already_initialized(client, db_session) -> None:
    from app.models import SiteSettings
    from app.services.auth_service import build_admin_user

    db_session.add(SiteSettings(blog_title="My Blog"))
    db_session.add(build_admin_user("admin", "secret123"))
    db_session.commit()

    with patch("app.routes.setup.ensure_database_exists"), patch("app.routes.setup.upgrade_database"):
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

If needed, add a session assertion test:

```python
def test_setup_submission_sets_session_after_success(client, db_session) -> None:
    with (
        patch("app.routes.setup.ensure_database_exists"),
        patch("app.routes.setup.upgrade_database"),
    ):
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

**Step 2: Run tests to verify failure if needed**

Run: `pytest tests/test_admin_auth.py::test_setup_submission_redirects_home_when_already_initialized tests/test_admin_auth.py::test_setup_submission_sets_session_after_success -v`
Expected: If the route internals changed incompatibly, this should expose it.

**Step 3: Write minimal implementation adjustments**

Only if the tests reveal regressions, make the smallest route changes necessary so:

- already-initialized POST still redirects to `/`
- successful POST still stores `request.session["user_id"]`
- no duplicate initialization occurs

Do not refactor unrelated auth or session code.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_admin_auth.py -v`
Expected: PASS.

---

### Task 6: Run focused regression suites for public/admin/setup behavior

**Files:**
- No code changes expected
- Test: `tests/test_public_pages.py`
- Test: `tests/test_admin_posts.py`
- Test: `tests/test_setup_service.py`
- Test: `tests/test_database_bootstrap_service.py`
- Test: `tests/test_admin_auth.py`

**Step 1: Run the focused regression suite**

Run: `pytest tests/test_database_bootstrap_service.py tests/test_setup_service.py tests/test_admin_auth.py tests/test_public_pages.py tests/test_admin_posts.py -v`
Expected: PASS.

**Step 2: If anything fails, fix one root cause at a time**

Use @superpowers:systematic-debugging before changing code. Do not batch speculative fixes.

**Step 3: Re-run the same focused suite**

Run: `pytest tests/test_database_bootstrap_service.py tests/test_setup_service.py tests/test_admin_auth.py tests/test_public_pages.py tests/test_admin_posts.py -v`
Expected: PASS with zero failures.

---

### Task 7: Run the full test suite as final verification

**Files:**
- No code changes expected

**Step 1: Run the full suite**

Run: `pytest -v`
Expected: PASS.

**Step 2: If the full suite fails, fix only the root cause revealed by the failing tests**

Use @superpowers:systematic-debugging before changing code. Re-run the specific failing tests first, then re-run `pytest -v`.

**Step 3: Record final verification evidence**

Capture the final passing command output in your response or notes so completion claims are backed by fresh evidence, following @superpowers:verification-before-completion.
