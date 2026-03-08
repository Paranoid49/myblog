from pathlib import Path

from playwright.sync_api import sync_playwright

output_dir = Path("project_logs/manual_checks")
output_dir.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("http://127.0.0.1:8000/admin/login")
    page.wait_for_load_state("networkidle")
    page.screenshot(path=str(output_dir / "debug-login-page.png"), full_page=True)
    (output_dir / "debug-login-page.html").write_text(page.content(), encoding="utf-8")

    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "secret123")
    page.click('button[type="submit"]', no_wait_after=True)
    page.wait_for_timeout(1000)

    page.screenshot(path=str(output_dir / "debug-after-login-click.png"), full_page=True)
    (output_dir / "debug-after-login-click.html").write_text(page.content(), encoding="utf-8")
    print(page.url)

    browser.close()
