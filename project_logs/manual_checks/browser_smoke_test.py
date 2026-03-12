from pathlib import Path

import httpx
from playwright.sync_api import TimeoutError, sync_playwright

BACKEND_URL = "http://127.0.0.1:8001"
FRONTEND_URL = "http://127.0.0.1:5175"
OUTPUT_FILE = Path("D:/projects/python/myblog/project_logs/manual_checks/browser_smoke_result.txt")
USERNAME = "admin"
PASSWORD = "secret123"


def ensure_initialized() -> None:
    with httpx.Client(timeout=20.0) as client:
        status_resp = client.get(f"{BACKEND_URL}/api/v1/setup/status")
        status_resp.raise_for_status()
        payload = status_resp.json()
        if payload["data"]["initialized"]:
            return

        setup_resp = client.post(
            f"{BACKEND_URL}/api/v1/setup",
            json={
                "blog_title": "自动化测试博客",
                "username": USERNAME,
                "password": PASSWORD,
                "confirm_password": PASSWORD,
            },
        )
        setup_resp.raise_for_status()
        result = setup_resp.json()
        if result.get("code") != 0:
            raise RuntimeError(f"setup_failed: {result}")


def main() -> None:
    ensure_initialized()

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. 登录
        page.goto(f"{FRONTEND_URL}/admin/login", wait_until="networkidle")
        page.locator('input[name="username"]').fill(USERNAME)
        page.locator('input[name="password"]').fill(PASSWORD)
        page.get_by_role("button", name="登录").click()
        page.wait_for_timeout(1000)
        page.wait_for_load_state("networkidle")
        try:
            page.wait_for_url("**/admin", timeout=10000)
        except TimeoutError:
            pass
        body = page.locator("body").inner_text()
        results.append(("login", page.url.endswith('/admin') and '概览' in body))

        # 2. 登录后访问 /admin/login 自动回跳
        page.goto(f"{FRONTEND_URL}/admin/login", wait_until="networkidle")
        try:
            page.wait_for_url("**/admin", timeout=10000)
        except TimeoutError:
            pass
        body = page.locator("body").inner_text()
        results.append(("login_redirect", page.url.endswith('/admin') and '概览' in body))

        # 3. 登录后从首页点击后台进入 /admin
        page.goto(FRONTEND_URL, wait_until="networkidle")
        page.get_by_role("link", name="后台").click()
        page.wait_for_timeout(1000)
        page.wait_for_load_state("networkidle")
        try:
            page.wait_for_url("**/admin", timeout=10000)
        except TimeoutError:
            pass
        body = page.locator("body").inner_text()
        results.append(("public_admin_entry", page.url.endswith('/admin') and '概览' in body))

        # 4. 新建文章
        page.goto(f"{FRONTEND_URL}/admin/posts", wait_until="networkidle")
        title = "自动化冒烟文章"
        content = "# 自动化冒烟文章\n\n这是浏览器冒烟测试创建的正文。"
        page.locator('input').nth(0).fill(title)
        page.locator('textarea').nth(1).fill(content)
        page.get_by_role("button", name="创建文章").click()
        page.wait_for_timeout(1000)
        page.wait_for_load_state("networkidle")
        body = page.locator("body").inner_text()
        results.append(("create_post", '文章已创建' in body or '自动化冒烟文章' in body))

        # 5. 发布文章
        page.get_by_role("button", name="发布").first.click()
        page.wait_for_timeout(1000)
        page.wait_for_load_state("networkidle")
        body = page.locator("body").inner_text()
        results.append(("publish_post", '文章已发布' in body or '已发布' in body))

        # 6. 前台查看文章详情
        page.goto(FRONTEND_URL, wait_until="networkidle")
        page.get_by_role("link", name=title).click()
        page.wait_for_timeout(1000)
        page.wait_for_load_state("networkidle")
        body = page.locator("body").inner_text()
        results.append(("view_post_detail", title in body))

        browser.close()

    OUTPUT_FILE.write_text(
        "\n".join([f"{name}={success}" for name, success in results]),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
