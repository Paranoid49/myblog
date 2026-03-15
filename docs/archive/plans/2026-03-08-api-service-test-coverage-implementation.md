# API and Service Full Coverage Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create and verify test cases for every HTTP endpoint and every public service function, each with at least one main-path and one key failure/boundary-path assertion.

**Architecture:** Use a layered test expansion strategy: enumerate all HTTP endpoints and public service functions first, then fill gaps with strict TDD in small batches (setup/public/admin first, then admin posts, then remaining services). Keep behavior-focused assertions and avoid implementation-coupled tests. Produce explicit mapping artifacts to prove no endpoint/function is omitted.

**Tech Stack:** FastAPI TestClient, pytest, unittest.mock, SQLAlchemy (SQLite test DB fixtures)

---

## Implementation Rules

- Follow @superpowers:test-driven-development for each behavior addition.
- Keep changes minimal and focused; no unrelated refactors.
- User policy forbids git write operations in this repo, so commit steps are intentionally omitted.
- Maintain a coverage mapping checklist throughout execution.

---

### Task 1: Build explicit coverage mapping artifacts

**Files:**
- Create: `docs/plans/2026-03-08-api-service-test-coverage-map.md`
- Read: `app/routes/public.py`
- Read: `app/routes/setup.py`
- Read: `app/routes/admin_auth.py`
- Read: `app/routes/admin_posts.py`
- Read: `app/main.py`
- Read: `app/services/*.py`

**Step 1: Enumerate HTTP endpoints**

Write a table in the mapping file:

```markdown
## Route Endpoint Mapping
| Endpoint | Method | Existing Test | Gap | Planned Test Name |
|---|---|---|---|---|
| / | GET | yes/no | ... | test_home_... |
```

Include every declared route decorator in `app/routes/*` and `/health` in `app/main.py`.

**Step 2: Enumerate public service functions**

Write another table:

```markdown
## Service Function Mapping
| Module | Function | Existing Test | Gap | Planned Test Name |
|---|---|---|---|---|
| app/services/setup_service.py | is_initialized | yes/no | ... | test_is_initialized_... |
```

Treat top-level non-underscore functions as public functions.

**Step 3: Mark current gaps only (no implementation yet)**

For each endpoint/function, mark if it already has:
- main-path test
- failure/boundary-path test

**Step 4: Verify mapping file completeness**

Manual verification: every route and every public service function appears exactly once.

---

### Task 2: Close HTTP gaps for setup/public/admin_auth/health chain

**Files:**
- Modify: `tests/test_public_pages.py`
- Modify: `tests/test_admin_auth.py`
- Modify: `tests/test_health.py`
- Update map: `docs/plans/2026-03-08-api-service-test-coverage-map.md`

**Step 1: Write one failing test for first uncovered endpoint behavior**

Example template:

```python
def test_<endpoint>_<behavior>(client) -> None:
    response = client.get("/path", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/setup"
```

**Step 2: Run only that test and confirm RED**

Run: `python -m pytest tests/<file>.py::test_<name> -v`
Expected: FAIL for the intended missing behavior.

**Step 3: Implement minimal code only if behavior is truly missing**

If behavior already exists and test fails due to assertion issue, fix test design instead of production code.

**Step 4: Re-run single test for GREEN**

Run same command; expected PASS.

**Step 5: Repeat steps 1-4 for each uncovered endpoint in this chain**

Cover at least:
- success path
- one key failure/redirect path

**Step 6: Run module-level regression**

Run:
- `python -m pytest tests/test_public_pages.py tests/test_admin_auth.py tests/test_health.py -v`
Expected: PASS.

**Step 7: Update mapping status**

Mark those endpoints as covered (main/failure both present).

---

### Task 3: Close HTTP gaps for admin_posts endpoints

**Files:**
- Modify: `tests/test_admin_posts.py`
- Update map: `docs/plans/2026-03-08-api-service-test-coverage-map.md`

**Step 1: Add failing tests for uncovered admin_posts endpoint behaviors**

For each uncovered endpoint in `admin_posts.py`, add focused tests for:
- main behavior (render/list/create/edit success)
- critical failure path (uninitialized redirect, auth redirect, not found)

**Step 2: Run each new test in isolation (RED)**

Run: `python -m pytest tests/test_admin_posts.py::test_<name> -v`
Expected: FAIL for intended reason.

**Step 3: Add minimal production code only if needed**

If route already meets behavior, keep production unchanged.

**Step 4: Re-run each isolated test (GREEN)**

Expected: PASS.

**Step 5: Run full admin_posts suite**

Run: `python -m pytest tests/test_admin_posts.py -v`
Expected: PASS.

**Step 6: Update mapping status**

Mark all admin_posts endpoints complete.

---

### Task 4: Close service-layer gaps for setup/database/migration/auth/post/taxonomy

**Files:**
- Modify existing service test files:
  - `tests/test_setup_service.py`
  - `tests/test_database_bootstrap_service.py`
  - `tests/test_post_service.py`
  - `tests/test_admin_auth.py` (if auth service tests are colocated)
- Create only if necessary:
  - `tests/test_taxonomy_service.py`
  - `tests/test_migration_service.py` (if separation improves clarity)
- Update map: `docs/plans/2026-03-08-api-service-test-coverage-map.md`

**Step 1: For each uncovered public service function, write a failing test first**

Template:

```python
def test_<function>_<boundary_behavior>() -> None:
    with pytest.raises(ExpectedError):
        function_under_test(...)
```

or

```python
def test_<function>_<main_behavior>(db_session) -> None:
    result = function_under_test(...)
    assert result == expected
```

**Step 2: Run each new test in isolation (RED)**

Run: `python -m pytest tests/<file>.py::test_<name> -v`
Expected: FAIL for intended missing behavior.

**Step 3: Implement minimal code only when required**

Do not refactor broadly.

**Step 4: Re-run isolated test (GREEN)**

Expected: PASS.

**Step 5: Run grouped service suites**

Run:
- `python -m pytest tests/test_setup_service.py tests/test_database_bootstrap_service.py tests/test_post_service.py -v`
- plus any new service test files if created
Expected: PASS.

**Step 6: Update mapping status**

Every public service function marked as covered for main + failure/boundary.

---

### Task 5: Add anti-regression checks for cwd-sensitive startup paths

**Files:**
- Modify: `tests/test_config.py`
- Modify: `tests/test_setup_service.py`
- Update map: `docs/plans/2026-03-08-api-service-test-coverage-map.md`

**Step 1: Ensure tests exist for all known cwd-sensitive boundaries**

Required checks:
- env file path absolute and stable
- templates directories absolute/existing
- migration config uses project-root alembic.ini
- migration script_location uses absolute migrations path

**Step 2: Add missing failing test if any boundary is not covered**

Run isolated test and confirm RED.

**Step 3: Implement minimal fix only if required**

Then rerun for GREEN.

**Step 4: Run boundary regression suite**

Run:
- `python -m pytest tests/test_config.py tests/test_setup_service.py -v`
Expected: PASS.

---

### Task 6: Prove full coverage completion with mapping + test runs

**Files:**
- Update: `docs/plans/2026-03-08-api-service-test-coverage-map.md`

**Step 1: Final mapping audit**

Confirm every endpoint/function row has:
- main-path test name
- failure/boundary-path test name
- status = complete

**Step 2: Run main-flow verification suite**

Run:
`python -m pytest tests/test_public_pages.py tests/test_admin_auth.py tests/test_admin_posts.py tests/test_setup_service.py tests/test_database_bootstrap_service.py tests/test_post_service.py tests/test_health.py tests/test_config.py -v`

Expected: PASS.

**Step 3: Run full regression**

Run:
`python -m pytest -v`

Expected: PASS.

**Step 4: Record final evidence in response**

Report:
- commands run
- pass/fail counts
- mapping completion confirmation
- any intentionally deferred items (if none, explicitly state none)
