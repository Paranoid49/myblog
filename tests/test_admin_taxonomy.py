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


def test_admin_can_update_category(client, logged_in_admin):
    """管理员可以重命名分类"""
    create_resp = client.post("/api/v1/admin/categories", json={"name": "旧名称"})
    cat_id = create_resp.json()["data"]["id"]
    update_resp = client.post(f"/api/v1/admin/categories/{cat_id}", json={"name": "新名称"})
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["name"] == "新名称"


def test_admin_can_delete_category(client, logged_in_admin):
    """管理员可以删除分类"""
    create_resp = client.post("/api/v1/admin/categories", json={"name": "待删除分类"})
    cat_id = create_resp.json()["data"]["id"]
    delete_resp = client.post(f"/api/v1/admin/categories/{cat_id}/delete")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["code"] == 0


def test_admin_can_update_tag(client, logged_in_admin):
    """管理员可以重命名标签"""
    create_resp = client.post("/api/v1/admin/tags", json={"name": "旧标签"})
    tag_id = create_resp.json()["data"]["id"]
    update_resp = client.post(f"/api/v1/admin/tags/{tag_id}", json={"name": "新标签"})
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["name"] == "新标签"


def test_admin_can_delete_tag(client, logged_in_admin):
    """管理员可以删除标签"""
    create_resp = client.post("/api/v1/admin/tags", json={"name": "待删除标签"})
    tag_id = create_resp.json()["data"]["id"]
    delete_resp = client.post(f"/api/v1/admin/tags/{tag_id}/delete")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["code"] == 0
