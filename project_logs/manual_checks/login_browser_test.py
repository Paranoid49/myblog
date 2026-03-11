from pathlib import Path

import httpx
from playwright.sync_api import TimeoutError, sync_playwright

BACKEND_URL = "http://127.0.0.1:8001"
FRONTEND_URL = "http://127.0.0.1:5175"
OUTPUT_FILE = Path("D:/projects/python/myblog/project_logs/manual_checks/login_browser_test_result.txt")
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
        setup_payload = setup_resp.json()
        if setup_payload.get("code") != 0:
            raise RuntimeError(f"setup_failed: {setup_payload}")


def main() -> None:
    ensure_initialized()

    request_info = {}
    response_info = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        def on_request(request):
            if "/api/v1/auth/login" in request.url:
                request_info["url"] = request.url
                request_info["method"] = request.method
                request_info["headers"] = request.headers
                request_info["post_data"] = request.post_data

        def on_response(response):
            if "/api/v1/auth/login" in response.url:
                response_info["status"] = response.status
                try:
                    response_info["text"] = response.text()
                except Exception as exc:
                    response_info["text"] = f"read_failed:{exc}"

        page.on("request", on_request)
        page.on("response", on_response)

        page.goto(f"{FRONTEND_URL}/admin/login", wait_until="networkidle")
        username_input = page.locator('input[type="text"]')
        password_input = page.locator('input[type="password"]')
        username_input.fill(USERNAME)
        password_input.fill(PASSWORD)
        page.wait_for_timeout(300)

        username_value = username_input.input_value()
        password_value = password_input.input_value()

        page.get_by_role("button", name="登录").click()
        page.wait_for_timeout(1500)
        page.wait_for_load_state("networkidle")

        try:
            page.wait_for_url("**/admin", timeout=10000)
        except TimeoutError:
            pass

        body_text = page.locator("body").inner_text()
        cookies = page.context.cookies()
        has_session_cookie = any(cookie.get("name") == "session" for cookie in cookies)
        stored_user = page.evaluate("() => window.localStorage.getItem('myblog_user')")
        error_text = ""
        try:
            error_node = page.locator(".notice.error")
            if error_node.count() > 0:
                error_text = error_node.first.inner_text()
        except Exception:
            error_text = ""

        api_login_resp = httpx.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            data={"username": USERNAME, "password": PASSWORD},
            timeout=20.0,
        )

        success = page.url.endswith("/admin") and has_session_cookie and bool(stored_user) and "概览" in body_text
        OUTPUT_FILE.write_text(
            "\n".join(
                [
                    f"username_value={username_value}",
                    f"password_value={password_value}",
                    f"url={page.url}",
                    f"has_session_cookie={has_session_cookie}",
                    f"has_local_user={bool(stored_user)}",
                    f"body_contains_dashboard={'概览' in body_text}",
                    f"page_error={error_text}",
                    f"request_url={request_info.get('url')}",
                    f"request_method={request_info.get('method')}",
                    f"request_content_type={request_info.get('headers', {}).get('content-type')}",
                    f"request_post_data={request_info.get('post_data')}",
                    f"response_status={response_info.get('status')}",
                    f"response_text={response_info.get('text')}",
                    f"api_login_http={api_login_resp.status_code}",
                    f"api_login_body={api_login_resp.text}",
                    f"success={success}",
                ]
            ),
            encoding="utf-8",
        )
        browser.close()


if __name__ == "__main__":
    main()
