from fastapi.testclient import TestClient


def test_root(client: TestClient):
    response = client.get("/api/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello, World!"}


def test_health(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "Ok"}


def test_error(client: TestClient):
    response = client.get("/api/error")
    assert response.status_code == 500
    assert response.text == "Internal server error"


def test_version(client: TestClient):
    response = client.get("/api/version")
    assert response.status_code == 200
    assert "version" in response.json()
