# Run Dev Config Summary Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make `scripts/run_dev.py` print a startup summary showing the actual app/debug settings plus a masked database configuration before launching uvicorn.

**Architecture:** Extend the existing `run_dev.py` script with a tiny formatting layer that reads `app.core.config.settings.database_url`, builds a masked URL plus split database fields, prints the summary, and then calls `uvicorn.run(...)` exactly as before. Keep this change local to the debug script and its tests.

**Tech Stack:** Python, argparse, uvicorn, SQLAlchemy URL parsing, pytest, unittest.mock, stdout capture

---

## Implementation Notes

- Follow @superpowers:test-driven-development for every behavior change: write the failing test first, watch it fail, then add the minimum code.
- Passwords must never be printed in clear text.
- Do not add connectivity checks, environment dumps, or verbose/debug flags in this task.
- User preference forbids git write operations in this repository, so commit steps are intentionally omitted from this plan.

---

### Task 1: Add tests for masked database summary output

**Files:**
- Modify: `tests/test_run_dev_script.py`
- Read for reference: `scripts/run_dev.py`
- Read for reference: `app/core/config.py`

**Step 1: Write the failing test**

Add a test that defines the desired printed startup summary:

```python
from unittest.mock import patch

from scripts.run_dev import main


def test_run_dev_prints_masked_database_summary(capsys) -> None:
    with (
        patch("scripts.run_dev.settings.database_url", "postgresql+psycopg://postgres:123456@localhost:5432/myblog"),
        patch("scripts.run_dev.uvicorn.run"),
    ):
        main([])

    output = capsys.readouterr().out
    assert "DATABASE_URL=postgresql+psycopg://postgres:***@localhost:5432/myblog" in output
    assert "DB_HOST=localhost" in output
    assert "DB_PORT=5432" in output
    assert "DB_NAME=myblog" in output
    assert "DB_USER=postgres" in output
    assert "123456" not in output
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_run_dev_script.py::test_run_dev_prints_masked_database_summary -v`
Expected: FAIL because `run_dev.py` does not print any summary yet.

**Step 3: Write minimal implementation**

In `scripts/run_dev.py`, add tiny helper functions to parse and print the database summary before `uvicorn.run(...)`:

```python
from sqlalchemy.engine import make_url

from app.core.config import settings


def build_masked_database_summary(database_url: str) -> list[str]:
    url = make_url(database_url)
    masked_url = str(url.set(password="***")) if url.password is not None else str(url)
    return [
        f"DATABASE_URL={masked_url}",
        f"DB_HOST={url.host}",
        f"DB_PORT={url.port}",
        f"DB_NAME={url.database}",
        f"DB_USER={url.username}",
    ]
```

Print these lines inside `main(...)` before the `uvicorn.run(...)` call.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_run_dev_script.py::test_run_dev_prints_masked_database_summary -v`
Expected: PASS.

---

### Task 2: Add tests for startup parameter summary output

**Files:**
- Modify: `tests/test_run_dev_script.py`
- Modify: `scripts/run_dev.py`

**Step 1: Write the failing test**

Add a second focused output test:

```python
def test_run_dev_prints_startup_parameters(capsys) -> None:
    with patch("scripts.run_dev.uvicorn.run"):
        main(["--port", "8001"])

    output = capsys.readouterr().out
    assert "APP=app.main:app" in output
    assert "HOST=127.0.0.1" in output
    assert "PORT=8001" in output
    assert "RELOAD=True" in output
    assert "LOG_LEVEL=debug" in output
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_run_dev_script.py::test_run_dev_prints_startup_parameters -v`
Expected: FAIL because the startup parameter summary is not printed yet.

**Step 3: Write minimal implementation**

Add a helper to `scripts/run_dev.py`:

```python
def build_startup_summary(port: int) -> list[str]:
    return [
        f"APP={DEFAULT_APP}",
        f"HOST={DEFAULT_HOST}",
        f"PORT={port}",
        "RELOAD=True",
        f"LOG_LEVEL={DEFAULT_LOG_LEVEL}",
    ]
```

Print these lines before the database summary and before `uvicorn.run(...)`.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_run_dev_script.py::test_run_dev_prints_startup_parameters -v`
Expected: PASS.

---

### Task 3: Add minimal invalid-URL fallback behavior

**Files:**
- Modify: `tests/test_run_dev_script.py`
- Modify: `scripts/run_dev.py`

**Step 1: Write the failing test**

Add a very small fallback test:

```python
def test_run_dev_prints_invalid_database_url_marker_when_url_cannot_be_parsed(capsys) -> None:
    with (
        patch("scripts.run_dev.settings.database_url", "not a valid database url"),
        patch("scripts.run_dev.uvicorn.run"),
    ):
        main([])

    output = capsys.readouterr().out
    assert "DATABASE_URL=<invalid>" in output
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_run_dev_script.py::test_run_dev_prints_invalid_database_url_marker_when_url_cannot_be_parsed -v`
Expected: FAIL if URL parsing exceptions are not handled.

**Step 3: Write minimal implementation**

Wrap the URL parsing summary in a tiny `try/except`:

```python
def build_masked_database_summary(database_url: str) -> list[str]:
    try:
        url = make_url(database_url)
    except Exception:
        return ["DATABASE_URL=<invalid>"]
```

Keep fallback behavior minimal. Do not add logging frameworks or extra diagnostics.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_run_dev_script.py::test_run_dev_prints_invalid_database_url_marker_when_url_cannot_be_parsed -v`
Expected: PASS.

---

### Task 4: Verify existing `uvicorn.run(...)` behavior is unchanged

**Files:**
- Modify: `tests/test_run_dev_script.py`
- Modify: `scripts/run_dev.py` only if tests expose regression

**Step 1: Run the existing script tests**

Run: `python -m pytest tests/test_run_dev_script.py::test_run_dev_uses_default_uvicorn_settings tests/test_run_dev_script.py::test_run_dev_allows_overriding_port tests/test_run_dev_script.py::test_run_dev_rejects_non_integer_port -v`
Expected: PASS.

**Step 2: If anything fails, fix only the regression**

Ensure the script still calls:

```python
uvicorn.run(
    "app.main:app",
    host="127.0.0.1",
    port=args.port,
    reload=True,
    log_level="debug",
)
```

Do not change the startup behavior beyond printing the summary.

**Step 3: Re-run the full script suite**

Run: `python -m pytest tests/test_run_dev_script.py -v`
Expected: PASS.

---

### Task 5: Run startup-related regression verification

**Files:**
- No code changes expected

**Step 1: Run startup-related tests**

Run: `python -m pytest tests/test_config.py tests/test_run_dev_script.py tests/test_health.py -v`
Expected: PASS.

**Step 2: Run the full suite**

Run: `python -m pytest -v`
Expected: PASS.

**Step 3: Record verification evidence**

Capture the passing command output in the final response, following @superpowers:verification-before-completion.
