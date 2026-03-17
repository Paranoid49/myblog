from pathlib import Path

import pytest

from app.models import Category, Tag

_FRONTEND_DIST = Path(__file__).resolve().parents[1] / "frontend" / "dist"
_skip_no_dist = pytest.mark.skipif(not _FRONTEND_DIST.exists(), reason="frontend/dist 未构建")


@_skip_no_dist
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
    update_resp = client.put(f"/api/v1/admin/categories/{cat_id}", json={"name": "新名称"})
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["name"] == "新名称"


def test_admin_can_delete_category(client, logged_in_admin):
    """管理员可以删除分类"""
    create_resp = client.post("/api/v1/admin/categories", json={"name": "待删除分类"})
    cat_id = create_resp.json()["data"]["id"]
    delete_resp = client.delete(f"/api/v1/admin/categories/{cat_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["code"] == 0


def test_admin_can_update_tag(client, logged_in_admin):
    """管理员可以重命名标签"""
    create_resp = client.post("/api/v1/admin/tags", json={"name": "旧标签"})
    tag_id = create_resp.json()["data"]["id"]
    update_resp = client.put(f"/api/v1/admin/tags/{tag_id}", json={"name": "新标签"})
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["name"] == "新标签"


def test_admin_can_delete_tag(client, logged_in_admin):
    """管理员可以删除标签"""
    create_resp = client.post("/api/v1/admin/tags", json={"name": "待删除标签"})
    tag_id = create_resp.json()["data"]["id"]
    delete_resp = client.delete(f"/api/v1/admin/tags/{tag_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["code"] == 0


# --- 边界测试 ---


def test_update_category_rejects_duplicate_name(client, logged_in_admin):
    """重命名分类为已存在的名称时返回 409"""
    client.post("/api/v1/admin/categories", json={"name": "分类A"})
    resp_b = client.post("/api/v1/admin/categories", json={"name": "分类B"})
    cat_b_id = resp_b.json()["data"]["id"]
    update_resp = client.put(f"/api/v1/admin/categories/{cat_b_id}", json={"name": "分类A"})
    assert update_resp.status_code == 409
    assert update_resp.json()["code"] == 1409


def test_update_tag_rejects_duplicate_name(client, logged_in_admin):
    """重命名标签为已存在的名称时返回 409"""
    client.post("/api/v1/admin/tags", json={"name": "标签A"})
    resp_b = client.post("/api/v1/admin/tags", json={"name": "标签B"})
    tag_b_id = resp_b.json()["data"]["id"]
    update_resp = client.put(f"/api/v1/admin/tags/{tag_b_id}", json={"name": "标签A"})
    assert update_resp.status_code == 409
    assert update_resp.json()["code"] == 1410


def test_delete_tag_removes_association_from_posts(client, logged_in_admin):
    """删除标签后，文章的标签列表不再包含该标签"""
    tag_resp = client.post("/api/v1/admin/tags", json={"name": "临时标签"})
    tag_id = tag_resp.json()["data"]["id"]
    post_resp = client.post("/api/v1/admin/posts", json={
        "title": "测试文章", "content": "内容", "tag_ids": [tag_id],
    })
    post_id = post_resp.json()["data"]["id"]
    # 发布文章使其可通过公开接口查询
    client.post(f"/api/v1/admin/posts/{post_id}/publish")
    post_slug = post_resp.json()["data"]["slug"]
    # 删除标签
    client.delete(f"/api/v1/admin/tags/{tag_id}")
    # 查询文章，标签列表应为空
    detail = client.get(f"/api/v1/posts/{post_slug}")
    assert detail.json()["data"]["tag_ids"] == []


def test_create_post_rejects_title_exceeding_max_length(client, logged_in_admin):
    """文章标题超过 200 字符时返回 422"""
    resp = client.post("/api/v1/admin/posts", json={
        "title": "A" * 201, "content": "内容",
    })
    assert resp.status_code == 422


def test_create_category_rejects_name_exceeding_max_length(client, logged_in_admin):
    """分类名称超过 100 字符时返回 422"""
    resp = client.post("/api/v1/admin/categories", json={"name": "A" * 101})
    assert resp.status_code == 422
