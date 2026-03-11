from app.models import SiteSettings


def test_api_get_author_profile_success(client, initialized_site, admin_user, db_session) -> None:
    initialized_site.author_name = "admin"
    initialized_site.author_bio = "这是我的个人独立博客"
    initialized_site.author_email = "admin@example.com"
    initialized_site.author_avatar = "https://example.com/avatar.png"
    initialized_site.author_link = "https://example.com/about"
    db_session.commit()

    response = client.get("/api/v1/author")

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["name"] == "admin"
    assert payload["data"]["bio"] == "这是我的个人独立博客"
    assert payload["data"]["email"] == "admin@example.com"
    assert payload["data"]["avatar"] == "https://example.com/avatar.png"
    assert payload["data"]["link"] == "https://example.com/about"


def test_api_update_author_profile_requires_login(client, initialized_site, admin_user) -> None:
    response = client.post(
        "/api/v1/author",
        json={
            "name": "新昵称",
            "bio": "新简介",
            "email": "new@example.com",
            "avatar": "https://example.com/new-avatar.png",
            "link": "https://example.com/new-link",
        },
    )

    assert response.status_code == 401
    payload = response.json()
    assert payload["code"] == 1002


def test_api_update_author_profile_success(client, logged_in_admin, initialized_site, db_session) -> None:
    response = client.post(
        "/api/v1/author",
        json={
            "name": "新昵称",
            "bio": "这是新的简介",
            "email": "new@example.com",
            "avatar": "https://example.com/new-avatar.png",
            "link": "https://example.com/new-link",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["name"] == "新昵称"
    assert payload["data"]["bio"] == "这是新的简介"
    assert payload["data"]["email"] == "new@example.com"
    assert payload["data"]["avatar"] == "https://example.com/new-avatar.png"
    assert payload["data"]["link"] == "https://example.com/new-link"

    settings = db_session.query(SiteSettings).one()
    assert settings.author_name == "新昵称"
    assert settings.author_bio == "这是新的简介"
    assert settings.author_email == "new@example.com"
    assert settings.author_avatar == "https://example.com/new-avatar.png"
    assert settings.author_link == "https://example.com/new-link"
