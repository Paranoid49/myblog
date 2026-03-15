# Home Redirect When Database Is Missing Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make requests to `/` redirect to `/setup` when the target PostgreSQL database does not exist, instead of failing with a database connection error.

**Architecture:** Extract the existing lightweight database existence check from `app/routes/setup.py` into a tiny reusable service, then make `app/routes/public.py` consult that service before opening a database session. Keep `get_db()` unchanged and only adjust the routes that need this pre-check.

**Tech Stack:** FastAPI, SQLAlchemy, psycopg/PostgreSQL URL parsing, pytest, unittest.mock

---

## Implementation Notes

- Follow @superpowers:test-driven-development strictly: every behavior change starts with a failing test.
- Keep this fix minimal. Do not redesign initialization flow, middleware, or dependency injection.
- User preference forbids git write operations in this repository, so commit steps are intentionally omitted from this plan.

---

### Task 1: Add homepage regression test for missing target database

**Files:**
- Modify: `tests/test_public_pages.py`
- Read for reference: `app/routes/public.py`
- Read for reference: `app/routes/setup.py`

**Step 1: Write the failing test**

Add a focused test that proves homepage requests redirect before trying to use the app database:

```python
from unittest.mock import patch


def test_home_redirects_to_setup_when_target_database_does_not_exist(client) -> None:
    with patch("app.routes.public.database_exists", return_value=False):
        response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/setup"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_public_pages.py::test_home_redirects_to_setup_when_target_database_does_not_exist -v`
Expected: FAIL because `app.routes.public` does not expose or use a database existence pre-check yet.

**Step 3: Write minimal implementation**

Do not touch `get_db()` yet. Only make the route capable of consulting a pre-check before opening a session.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_public_pages.py::test_home_redirects_to_setup_when_target_database_does_not_exist -v`
Expected: PASS.

---

### Task 2: Extract reusable database existence check service

**Files:**
- Create: `app/services/database_state_service.py`
- Modify: `app/routes/setup.py`
- Modify: `app/routes/public.py`
- Read for reference: `app/core/config.py`

**Step 1: Write the failing service-level test indirectly through route behavior**

Reuse the failing route test from Task 1 as the safety net. No additional broad test surface is needed for this small extraction.

**Step 2: Write minimal implementation**

Create `app/services/database_state_service.py` with the existing lightweight PostgreSQL-aware logic:

```python
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.core.config import settings


def database_exists() -> bool:
    url = make_url(settings.database_url)
    if not url.drivername.startswith("postgresql"):
        return True

    engine = create_engine(str(url.set(database="postgres")), future=True)
    try:
        with engine.connect() as connection:
            return bool(
                connection.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
                    {"database_name": url.database},
                ).scalar()
            )
    except Exception:
        return False
    finally:
        engine.dispose()
```

Then update:

- `app/routes/setup.py` to import and use `database_exists` from the new service
- `app/routes/public.py` to import the same function and check it before opening a database session

In `app/routes/public.py`, change the homepage route shape to avoid opening a session in the function signature:

```python
from app.core.db import SessionLocal
from app.services.database_state_service import database_exists


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    if not database_exists():
        return RedirectResponse(url="/setup", status_code=302)

    db = SessionLocal()
    try:
        if not is_initialized(db):
            return RedirectResponse(url="/setup", status_code=302)

        posts = list_published_posts(db)
        site_settings = get_site_settings(db)
        site_title = site_settings.blog_title if site_settings else None
        return templates.TemplateResponse(request, "public/index.html", {"posts": posts, "site_title": site_title})
    finally:
        db.close()
```

Keep all other public routes unchanged unless a test proves they need adjustment.

**Step 3: Run focused tests to verify behavior**

Run: `python -m pytest tests/test_public_pages.py::test_home_redirects_to_setup_when_target_database_does_not_exist tests/test_public_pages.py::test_home_redirects_to_setup_when_uninitialized tests/test_public_pages.py::test_home_displays_database_blog_title_when_initialized -v`
Expected: PASS.

---

### Task 3: Verify setup behavior still works with extracted service

**Files:**
- Modify only if tests expose regression: `app/routes/setup.py`
- Test: `tests/test_admin_auth.py`

**Step 1: Run setup-related regression tests**

Run: `python -m pytest tests/test_admin_auth.py::test_setup_page_is_available_when_target_database_does_not_exist tests/test_admin_auth.py::test_setup_submission_bootstraps_database_before_migration_and_initialization tests/test_admin_auth.py::test_setup_submission_shows_generic_error_when_bootstrap_fails -v`
Expected: PASS.

**Step 2: If anything fails, fix only the extraction regression**

Do not redesign route flow. Only correct imports or patch targets introduced by moving `database_exists`.

**Step 3: Re-run the same setup-related tests**

Run: `python -m pytest tests/test_admin_auth.py::test_setup_page_is_available_when_target_database_does_not_exist tests/test_admin_auth.py::test_setup_submission_bootstraps_database_before_migration_and_initialization tests/test_admin_auth.py::test_setup_submission_shows_generic_error_when_bootstrap_fails -v`
Expected: PASS.

---

### Task 4: Run full regression verification

**Files:**
- No code changes expected

**Step 1: Run route-focused regression suite**

Run: `python -m pytest tests/test_public_pages.py tests/test_admin_auth.py -v`
Expected: PASS.

**Step 2: Run the full test suite**

Run: `python -m pytest -v`
Expected: PASS.

**Step 3: Record verification evidence**

Capture the passing command output in the final response, following @superpowers:verification-before-completion.
