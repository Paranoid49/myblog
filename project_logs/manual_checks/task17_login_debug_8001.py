from pathlib import Path

from playwright.sync_api import sync_playwright

output_dir = Path("project_logs/manual_checks")
output_dir.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    def log_response(response):
        if response.status >= 400:
            print("RESPONSE", response.status, response.url)

    page.on("response", log_response)

    page.goto("http://127.0.0.1:8001/admin/login")
    page.wait_for_load_state("networkidle")
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "secret123")
    page.click('button[type="submit"]', no_wait_after=True)
    page.wait_for_timeout(2000)

    print("URL", page.url)
    print(page.content()[:500])

    browser.close()
