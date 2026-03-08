from pathlib import Path

from playwright.sync_api import sync_playwright

output_dir = Path("project_logs/manual_checks")
output_dir.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("http://127.0.0.1:8000/admin/login")
    page.wait_for_load_state("networkidle")
    page.screenshot(path=str(output_dir / "admin-login.png"), full_page=True)

    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "secret123")
    page.click('button[type="submit"]', no_wait_after=True)
    page.wait_for_url("**/admin/posts")
    page.wait_for_load_state("networkidle")
    page.screenshot(path=str(output_dir / "admin-post-list.png"), full_page=True)

    page.click('a[href="/admin/posts/new"]')
    page.wait_for_url("**/admin/posts/new")
    page.wait_for_load_state("networkidle")
    page.screenshot(path=str(output_dir / "admin-new-post.png"), full_page=True)

    page.fill('input[name="title"]', "浏览器验收文章")
    page.fill('textarea[name="summary"]', "manual summary")
    page.fill('textarea[name="content"]', "manual content")
    page.select_option('select[name="category_id"]', label="Python")
    page.check('input[name="tag_ids"]')
    page.click('button[type="submit"]', no_wait_after=True)
    page.wait_for_url("**/admin/posts")
    page.wait_for_load_state("networkidle")
    page.screenshot(path=str(output_dir / "admin-post-list-after-create.png"), full_page=True)

    page.click('a[href^="/admin/posts/"][href$="/edit"]')
    page.wait_for_url("**/edit")
    page.wait_for_load_state("networkidle")
    page.screenshot(path=str(output_dir / "admin-edit-post.png"), full_page=True)

    page.fill('input[name="title"]', "浏览器验收文章-已更新")
    page.fill('textarea[name="content"]', "manual content updated")
    page.click('button[type="submit"]', no_wait_after=True)
    page.wait_for_url("**/admin/posts")
    page.wait_for_load_state("networkidle")
    page.screenshot(path=str(output_dir / "admin-post-list-after-edit.png"), full_page=True)

    page.goto("http://127.0.0.1:8000/")
    page.wait_for_load_state("networkidle")
    page.screenshot(path=str(output_dir / "public-home.png"), full_page=True)

    browser.close()
