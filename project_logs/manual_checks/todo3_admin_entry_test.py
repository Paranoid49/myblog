from pathlib import Path

from playwright.sync_api import TimeoutError, sync_playwright

BASE_URL = "http://127.0.0.1:8001"
OUTPUT_FILE = Path("D:/projects/python/myblog/project_logs/manual_checks/todo3_admin_entry_result.txt")


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 未登录时首页后台入口应去登录页
        page.goto(BASE_URL, wait_until="networkidle")
        anonymous_href = page.get_by_role("link", name="后台").get_attribute("href")
        page.get_by_role("link", name="后台").click()
        page.wait_for_timeout(1000)
        page.wait_for_load_state("networkidle")
        anonymous_login = page.url.endswith("/admin/login")

        # 登录后后台入口应去 /admin
        page.locator('input[name="username"]').fill("admin")
        page.locator('input[name="password"]').fill("secret123")
        page.get_by_role("button", name="登录").click()
        page.wait_for_timeout(1000)
        page.wait_for_load_state("networkidle")
        try:
            page.wait_for_url("**/admin", timeout=10000)
        except TimeoutError:
            pass

        page.goto(BASE_URL, wait_until="networkidle")
        logged_in_href = page.get_by_role("link", name="后台").get_attribute("href")
        page.get_by_role("link", name="后台").click()
        page.wait_for_timeout(1000)
        page.wait_for_load_state("networkidle")
        try:
            page.wait_for_url("**/admin", timeout=10000)
        except TimeoutError:
            pass
        logged_in_admin = page.url.endswith("/admin") and "概览" in page.locator("body").inner_text()

        # 已登录访问 /admin/login 自动回跳
        page.goto(f"{BASE_URL}/admin/login", wait_until="networkidle")
        try:
            page.wait_for_url("**/admin", timeout=10000)
        except TimeoutError:
            pass
        login_redirect = page.url.endswith("/admin") and "概览" in page.locator("body").inner_text()

        OUTPUT_FILE.write_text(
            "\n".join(
                [
                    f"anonymous_href={anonymous_href}",
                    f"anonymous_login={anonymous_login}",
                    f"logged_in_href={logged_in_href}",
                    f"logged_in_admin={logged_in_admin}",
                    f"login_redirect={login_redirect}",
                    f"success={anonymous_href == '/admin/login' and anonymous_login and logged_in_href == '/admin' and logged_in_admin and login_redirect}",
                ]
            ),
            encoding="utf-8",
        )
        browser.close()


if __name__ == "__main__":
    main()
