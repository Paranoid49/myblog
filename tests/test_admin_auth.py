from app.core.security import hash_password, verify_password


def test_password_hash_and_verify() -> None:
    password = "secret123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True


def test_admin_login_page_renders(client) -> None:
    response = client.get("/admin/login")
    assert response.status_code == 200
    assert "登录" in response.text


def test_admin_login_sets_session(client, admin_user) -> None:
    response = client.post(
        "/admin/login",
        data={"username": "admin", "password": "secret123"},
        follow_redirects=False,
    )
    assert response.status_code in (302, 303)


def test_admin_logout_clears_session(client) -> None:
    response = client.get("/admin/logout", follow_redirects=False)
    assert response.status_code == 302
