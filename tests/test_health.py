from fastapi.testclient import TestClient

from app.main import app


def test_health_route_exists():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_route_rejects_post_method() -> None:
    client = TestClient(app)
    response = client.post("/health")
    assert response.status_code == 405
