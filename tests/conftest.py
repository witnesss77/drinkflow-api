import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.cfg import tests_db_url
from core.models.models import Base
from fastapi.testclient import TestClient
from core.main import app


engine = create_async_engine(tests_db_url)

TestingSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)


@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)

@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def create_drink(test_client):
    obj = {
            "name": "test",
            "desc": "test",
            "alcoholic": True,
            "price": 111,
            "factory_id": 1,
    }
    request = test_client.post('/drinks', json = obj)
    return request.json()["id"]


@pytest.fixture
def create_warehouse(test_client) -> int:
    response = test_client.post(
        "/warehouses",
        json={
            "name": "test warehouse",
            "address": "test location"
        }
    )

    return response.json()["id"]

@pytest.fixture
def refresh_token(test_client):
    payload = {
        "username": "str",
        "password": "12345678",
    }

    response = test_client.post("/auth/token", data=payload)
    assert response.status_code == 200

    return response.json()["refresh_token"]