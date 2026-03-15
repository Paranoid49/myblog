# Run Dev Script Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a simple local development startup script so the app can be launched with one command for debugging, while still allowing a minimal `--port` override.

**Architecture:** Add a small `scripts/run_dev.py` wrapper around `uvicorn.run(...)` with fixed local-development defaults for app import path, host, reload, and debug logging. Keep the script intentionally narrow: parse only an optional `--port` argument, then pass the resolved values into `uvicorn.run`.

**Tech Stack:** Python, argparse, uvicorn, pytest, unittest.mock

---

## Implementation Notes

- Follow @superpowers:test-driven-development for each behavior: write the test first, watch it fail, then write the minimum implementation.
- This script is for **local development only**. Do not add production concerns.
- Keep the interface intentionally small. Only support `--port` beyond the defaults.
- User preference forbids git write operations in this repository, so commit steps are intentionally omitted from this plan.

---

### Task 1: Add contract tests for the dev startup script entrypoint

**Files:**
- Create: `tests/test_run_dev_script.py`
- Read for reference: `scripts/create_admin.py`

**Step 1: Write the failing tests**

Create `tests/test_run_dev_script.py` with a test that defines the desired default behavior:

```python
from unittest.mock import patch

from scripts.run_dev import main


def test_run_dev_uses_default_uvicorn_settings() -> None:
    with patch("scripts.run_dev.uvicorn.run") as mock_run:
        main([])

    mock_run.assert_called_once_with(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="debug",
    )
```

Add a second test for the only supported override:

```python
def test_run_dev_allows_overriding_port() -> None:
    with patch("scripts.run_dev.uvicorn.run") as mock_run:
        main(["--port", "8001"])

    mock_run.assert_called_once_with(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="debug",
    )
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_run_dev_script.py -v`
Expected: FAIL because `scripts/run_dev.py` does not exist yet.

**Step 3: Write minimal implementation**

Create `scripts/run_dev.py` with a narrow entrypoint:

```python
import argparse

import uvicorn


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_APP = "app.main:app"
DEFAULT_LOG_LEVEL = "debug"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    uvicorn.run(
        DEFAULT_APP,
        host=DEFAULT_HOST,
        port=args.port,
        reload=True,
        log_level=DEFAULT_LOG_LEVEL,
    )


if __name__ == "__main__":
    main()
```

Do not add host flags, browser opening, environment probing, or setup automation.

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_run_dev_script.py -v`
Expected: PASS.

---

### Task 2: Add a small CLI behavior test for invalid port input

**Files:**
- Modify: `tests/test_run_dev_script.py`
- Modify: `scripts/run_dev.py`

**Step 1: Write the failing test**

Add one focused CLI test to prove argument parsing stays standard and simple:

```python
import pytest

from scripts.run_dev import main


def test_run_dev_rejects_non_integer_port() -> None:
    with pytest.raises(SystemExit):
        main(["--port", "not-a-number"])
```

**Step 2: Run the focused test to verify behavior**

Run: `python -m pytest tests/test_run_dev_script.py::test_run_dev_rejects_non_integer_port -v`
Expected: PASS if `argparse` is wired correctly, or FAIL if parsing is not yet implemented through `argparse`.

**Step 3: Write minimal implementation only if needed**

If the test fails, keep parsing delegated to `argparse` with `type=int`. Do not add custom validation layers.

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_run_dev_script.py -v`
Expected: PASS.

---

### Task 3: Verify the script works from the command line without starting a real server in tests

**Files:**
- No new code expected
- Test: `tests/test_run_dev_script.py`

**Step 1: Run the script test suite**

Run: `python -m pytest tests/test_run_dev_script.py -v`
Expected: PASS.

**Step 2: Perform a manual smoke check locally**

Run one of these commands manually outside pytest:

```bash
python scripts/run_dev.py
```

or

```bash
python scripts/run_dev.py --port 8001
```

Expected:
- Uvicorn starts successfully
- App import path is `app.main:app`
- Server binds to `127.0.0.1` on the selected port
- Reload is enabled
- Debug logging is enabled

**Step 3: Stop the server after confirming startup**

Use `Ctrl+C` after verifying the startup banner.

---

### Task 4: Run the full test suite as regression verification

**Files:**
- No code changes expected

**Step 1: Run the full suite**

Run: `python -m pytest -v`
Expected: PASS.

**Step 2: If anything fails, fix only the revealed root cause**

Use @superpowers:systematic-debugging before changing code. Do not batch speculative fixes.

**Step 3: Record verification evidence**

Capture the final passing test output in your response or notes, following @superpowers:verification-before-completion.
