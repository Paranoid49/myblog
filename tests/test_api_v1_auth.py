from conftest import CSRF_HEADERS
from fastapi.testclient import TestClient

from app.core.rate_limiter import login_limiter
from app.main import app as fastapi_app


def _form(client, **kwargs):
    return kwargs


def test_api_auth_login_success(client, initialized_site, admin_user) -> None:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "secret123"},
        headers=CSRF_HEADERS,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["username"] == "admin"


def test_api_auth_login_rejects_invalid_credentials(client, initialized_site, admin_user) -> None:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "wrong"},
        headers=CSRF_HEADERS,
    )

    assert response.status_code == 401
    payload = response.json()
    assert payload["code"] == 1003


def test_api_auth_logout_clears_session(client, initialized_site, admin_user, seeded_category) -> None:
    login = client.post("/api/v1/auth/login", data={"username": "admin", "password": "secret123"}, headers=CSRF_HEADERS)
    assert login.status_code == 200

    logout = client.post("/api/v1/auth/logout", headers=CSRF_HEADERS)
    assert logout.status_code == 200

    create_after_logout = client.post(
        "/api/v1/admin/posts",
        json={
            "title": "Should Fail",
            "summary": "s",
            "content": "c",
            "category_id": seeded_category.id,
            "tag_ids": [],
        },
        headers=CSRF_HEADERS,
    )
    assert create_after_logout.status_code == 401


def test_login_rate_limit_blocks_after_max_attempts(client, initialized_site, admin_user):
    """连续多次登录失败后被速率限制拦截"""
    login_limiter.reset("testclient")  # 重置测试客户端的限制状态

    for _ in range(5):
        client.post("/api/v1/auth/login", data={"username": "admin", "password": "wrong"})

    # 第 6 次应该被拦截
    resp = client.post("/api/v1/auth/login", data={"username": "admin", "password": "wrong"})
    assert resp.status_code == 429
    assert resp.json()["code"] == 1006

    login_limiter.reset("testclient")  # 清理


def test_post_without_csrf_header_is_rejected(initialized_site, admin_user):
    """不带 CSRF 头的 POST 请求被拒绝"""
    # 使用原生 TestClient（不自动注入 CSRF 头）
    with TestClient(fastapi_app) as raw_client:
        resp = raw_client.post(
            "/api/v1/auth/login",
            data={"username": "admin", "password": "secret123"},
        )
    assert resp.status_code == 403
    assert resp.json()["code"] == 1005
