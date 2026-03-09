from app.models import Category, Tag


def test_taxonomy_page_requires_login(client, initialized_site, admin_user) -> None:
    response = client.get("/admin/taxonomy", follow_redirects=False)

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/admin/login"


def test_taxonomy_page_renders(client, logged_in_admin, seeded_category, seeded_tags) -> None:
    response = client.get("/admin/taxonomy")

    assert response.status_code == 200
    assert "分类与标签" in response.text
    assert "Python" in response.text
    assert "FastAPI" in response.text


def test_admin_can_create_category(client, logged_in_admin, db_session) -> None:
    response = client.post("/admin/categories", data={"name": "数据库"}, follow_redirects=False)

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/admin/taxonomy"

    category = db_session.query(Category).filter(Category.slug == "shu-ju-ku").one_or_none()
    assert category is not None


def test_admin_can_create_tag(client, logged_in_admin, db_session) -> None:
    response = client.post("/admin/tags", data={"name": "后端"}, follow_redirects=False)

    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/admin/taxonomy"

    tag = db_session.query(Tag).filter(Tag.slug == "hou-duan").one_or_none()
    assert tag is not None


def test_create_category_rejects_duplicate_slug(client, logged_in_admin, seeded_category) -> None:
    response = client.post("/admin/categories", data={"name": "python"})

    assert response.status_code == 400
    assert "分类已存在" in response.text


def test_create_tag_rejects_empty_name(client, logged_in_admin) -> None:
    response = client.post("/admin/tags", data={"name": "   "})

    assert response.status_code == 400
    assert "标签名称不能为空" in response.text
