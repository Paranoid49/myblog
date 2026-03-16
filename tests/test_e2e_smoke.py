import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from unittest.mock import patch

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TIMEOUT = 30.0


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_http_ready(url: str, timeout: float = DEFAULT_TIMEOUT) -> None:
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=2) as response:
                if response.status < 500:
                    return
        except (HTTPError, URLError, OSError) as exc:
            last_error = exc
        time.sleep(0.2)
    raise AssertionError(f"服务未就绪: {url}, last_error={last_error}")


def _post_json(url: str, payload: dict) -> dict:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        },
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def test_admin_posts_redirects_to_login_and_returns_after_login(tmp_path) -> None:
    playwright = pytest.importorskip("playwright.sync_api")

    backend_port = _find_free_port()
    backend_url = f"http://127.0.0.1:{backend_port}"
    database_path = tmp_path / "page-smoke.db"
    env = {
        **os.environ,
        "DATABASE_URL": f"sqlite:///{database_path}",
        "SECRET_KEY": "test-secret-key!",
    }

    backend_process = subprocess.Popen(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "start_blog.py"),
            "--port",
            str(backend_port),
        ],
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        _wait_for_http_ready(f"{backend_url}/api/v1/setup/status")

        setup_payload = _post_json(
            f"{backend_url}/api/v1/setup",
            {
                "blog_title": "页面冒烟测试博客",
                "username": "admin",
                "password": "secret123",
                "confirm_password": "secret123",
            },
        )
        assert setup_payload["code"] == 0

        with playwright.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(f"{backend_url}/admin/posts", wait_until="networkidle")
                page.wait_for_url(f"{backend_url}/admin/login", timeout=10000)
                assert "登录" in page.locator("body").inner_text()

                page.locator('input[name="username"]').fill("admin")
                page.locator('input[name="password"]').fill("secret123")
                page.get_by_role("button", name="登录").click()

                page.wait_for_url(f"{backend_url}/admin/posts", timeout=10000)
                body = page.locator("body").inner_text()
                assert "文章管理" in body
            finally:
                browser.close()
    finally:
        if backend_process.poll() is None:
            backend_process.terminate()
            try:
                backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_process.kill()
                backend_process.wait(timeout=5)


def test_logout_redirects_back_to_admin_login(tmp_path) -> None:
    playwright = pytest.importorskip("playwright.sync_api")

    backend_port = _find_free_port()
    backend_url = f"http://127.0.0.1:{backend_port}"
    database_path = tmp_path / "logout-smoke.db"
    env = {
        **os.environ,
        "DATABASE_URL": f"sqlite:///{database_path}",
        "SECRET_KEY": "test-secret-key!",
    }

    backend_process = subprocess.Popen(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "start_blog.py"),
            "--port",
            str(backend_port),
        ],
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        _wait_for_http_ready(f"{backend_url}/api/v1/setup/status")

        setup_payload = _post_json(
            f"{backend_url}/api/v1/setup",
            {
                "blog_title": "页面冒烟测试博客",
                "username": "admin",
                "password": "secret123",
                "confirm_password": "secret123",
            },
        )
        assert setup_payload["code"] == 0

        with playwright.sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(f"{backend_url}/admin/login", wait_until="networkidle")
                page.locator('input[name="username"]').fill("admin")
                page.locator('input[name="password"]').fill("secret123")
                page.get_by_role("button", name="登录").click()

                page.wait_for_url(f"{backend_url}/admin", timeout=10000)
                page.get_by_role("button", name="退出登录").click()

                page.wait_for_url(f"{backend_url}/admin/login", timeout=10000)
                assert "登录" in page.locator("body").inner_text()
            finally:
                browser.close()
    finally:
        if backend_process.poll() is None:
            backend_process.terminate()
            try:
                backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_process.kill()
                backend_process.wait(timeout=5)


def test_minimal_flow_setup_login_create_publish_and_home_visible(client, db_session) -> None:
    with patch("app.routes.api_v1_setup.upgrade_database"):
        setup_resp = client.post(
            "/api/v1/setup",
            json={
                "blog_title": "我的博客",
                "username": "admin",
                "password": "secret123",
                "confirm_password": "secret123",
            },
        )
    assert setup_resp.status_code == 200
    assert setup_resp.json()["code"] == 0

    taxonomy_response = client.post("/api/v1/admin/categories", json={"name": "Python"})
    assert taxonomy_response.status_code == 201
    category_id = taxonomy_response.json()["data"]["id"]

    create_resp = client.post(
        "/api/v1/admin/posts",
        json={
            "title": "E2E 文章",
            "summary": "摘要",
            "content": "# 正文\n\n这是内容",
            "category_id": category_id,
            "tag_ids": [],
        },
    )
    assert create_resp.status_code == 201
    post_id = create_resp.json()["data"]["id"]

    publish_resp = client.post(f"/api/v1/admin/posts/{post_id}/publish")
    assert publish_resp.status_code == 200

    home = client.get("/")
    assert home.status_code == 200
    assert '<div id="root"></div>' in home.text

    list_resp = client.get("/api/v1/posts")
    assert list_resp.status_code == 200
    payload = list_resp.json()
    assert any(item["title"] == "E2E 文章" for item in payload["data"]["items"])
