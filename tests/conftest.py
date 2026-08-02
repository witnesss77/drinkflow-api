import pytest

from fastapi.testclient import TestClient
from core.main import app

@pytest.fixture
def test_client():
    return TestClient(app)