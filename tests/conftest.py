import pytest

from fastapi.testclient import TestClient
from core.main import app

@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)

@pytest.fixture
def refresh_token(test_client):
    payload = {
        "username": "str",
        "password": "12345678",
    }

    response = test_client.post("/auth/token", data=payload)
    assert response.status_code == 200

    return response.json()["refresh_token"]