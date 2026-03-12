from pathlib import Path

from playwright.sync_api import TimeoutError, sync_playwright

BASE_URL = "http://127.0.0.1:8001"
OUTPUT_FILE = Path("D:/projects/python/myblog/project_logs/manual_checks/todo5_auth_experience_result.txt")


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 登录
        page.goto(f"{BASE_URL}/admin/login", wait_until="networkidle")
        page.locator('input[name="username"]').fill("admin")
        page.locator('input[name="password"]').fill("secret123")
        page.get_by_role("button", name="登录").click()
        page.wait_for_timeout(1000)
        page.wait_for_load_state("networkidle")
        try:
            page.wait_for_url("**/admin", timeout=10000)
        except TimeoutError:
            pass
        login_ok = page.url.endswith('/admin') and '概览' in page.locator('body').inner_text()

        # 刷新后台页面
        page.reload(wait_until="networkidle")
        refresh_ok = page.url.endswith('/admin') and '概览' in page.locator('body').inner_text()

        # 访问登录页自动回跳
        page.goto(f"{BASE_URL}/admin/login", wait_until="networkidle")
        try:
            page.wait_for_url("**/admin", timeout=10000)
        except TimeoutError:
            pass
        login_redirect_ok = page.url.endswith('/admin') and '概览' in page.locator('body').inner_text()

        # 退出登录
        page.get_by_role('button', name='退出登录').click()
        page.wait_for_timeout(1000)
        page.wait_for_load_state('networkidle')
        logout_ok = page.url.endswith('/admin/login')

        # 登出后首页后台入口
        page.goto(BASE_URL, wait_until='networkidle')
        admin_href_after_logout = page.get_by_role('link', name='后台').get_attribute('href')
        logout_link_ok = admin_href_after_logout == '/admin/login'

        OUTPUT_FILE.write_text(
            '\n'.join([
                f'login_ok={login_ok}',
                f'refresh_ok={refresh_ok}',
                f'login_redirect_ok={login_redirect_ok}',
                f'logout_ok={logout_ok}',
                f'logout_link_ok={logout_link_ok}',
                f'success={all([login_ok, refresh_ok, login_redirect_ok, logout_ok, logout_link_ok])}',
            ]),
            encoding='utf-8',
        )
        browser.close()


if __name__ == '__main__':
    main()
