from conftest import CSRF_HEADERS


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
