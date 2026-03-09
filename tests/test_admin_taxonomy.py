from app.models import Category, Tag


def test_admin_taxonomy_route_is_served_by_frontend_spa(client, initialized_site, admin_user) -> None:
    response = client.get("/admin/taxonomy")

    assert response.status_code == 200
    assert '<div id="root"></div>' in response.text


def test_admin_can_create_category(client, logged_in_admin, db_session) -> None:
    response = client.post("/api/v1/admin/categories", json={"name": "数据库"})

    assert response.status_code == 201

    category = db_session.query(Category).filter(Category.slug == "shu-ju-ku").one_or_none()
    assert category is not None


def test_admin_can_create_tag(client, logged_in_admin, db_session) -> None:
    response = client.post("/api/v1/admin/tags", json={"name": "后端"})

    assert response.status_code == 201

    tag = db_session.query(Tag).filter(Tag.slug == "hou-duan").one_or_none()
    assert tag is not None


def test_create_category_rejects_duplicate_slug(client, logged_in_admin, seeded_category) -> None:
    response = client.post("/api/v1/admin/categories", json={"name": "python"})

    assert response.status_code == 409
    assert response.json()["code"] == 1409


def test_create_tag_rejects_empty_name(client, logged_in_admin) -> None:
    response = client.post("/api/v1/admin/tags", json={"name": "   "})

    assert response.status_code == 422
    payload = response.json()
    assert payload["detail"]
