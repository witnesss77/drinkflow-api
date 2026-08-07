import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from core.cfg import tests_db_url
import uuid
import random
from core.models.models import Base
from fastapi.testclient import TestClient
from core.auth.router import get_current_user
from core.main import app
from core.models.database import get_session

engine = create_async_engine(tests_db_url, poolclass = NullPool)

TestingSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

@pytest.fixture
def override_get_session():

    async def _override():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = _override
    yield
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
async def clear_database():
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())

    yield


@pytest.fixture
def test_client(override_get_session) -> TestClient:
    return TestClient(app)

@pytest.fixture(scope="session", autouse=True)
async def prepare_database():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def get_testing_session():
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
def create_drink(test_client, create_factory):
    obj = {
            "name": "test",
            "desc": "test",
            "alcoholic": True,
            "price": 111,
            "factory_id": create_factory,
    }
    request = test_client.post('/drinks', json = obj)
    return request.json()["id"]

@pytest.fixture
def create_factory(test_client):
    obj = {
            "name": "test",
            "location": "piter"
    }
    request = test_client.post('/factories', json = obj)
    return request.json()["id"]



@pytest.fixture
def create_warehouse(test_client):
    response = test_client.post(
        "/warehouses",
        json={
            "name": "test warehouse",
            "address": "test location"
        }
    )
    
    return response.json()["id"]

@pytest.fixture
def create_order(test_client, create_user, create_warehouse):
    obj = {
        "user_id": create_user,
        "warehouse_id": create_warehouse,
    }

    request = test_client.post('/orders', json=obj)
    print(request.text)
    return request.json()["id"]


@pytest.fixture
def create_order_item(
    test_client,
    create_drink,
    create_order,
    create_user,
    create_warehouse,
    create_stock
):

    obj = {
        "order_id": create_order,
        "user_id": create_user,
        "drink_id": create_drink,
        "quantity": 10,
        "price_per_item": 100
    }

    response = test_client.post(
        "/orders/order_items",
        params={
            "warehouse_id": create_warehouse
        },
        json=obj
    )

    print(response.text)
    return response.json()["id"]
@pytest.fixture
def create_stock(test_client, create_drink, create_warehouse):
    obj = {
        "drink_id": create_drink,
        "warehouse_id": create_warehouse,
        "quantity": 100,
        "reserved_quantity": 0
    }
    response = test_client.post("/stocks",json=obj)

    print(response.text)
    return response.json()["id"]

def create_order_stock(test_client, drink_id, warehouse_id):
    obj = {
        "drink_id": drink_id,
        "warehouse_id": warehouse_id,
        "quantity": 100,
        "reserved_quantity": 0
    }

    request = test_client.post("/stocks", json=obj)
    print(request.text)
    return request.json()["id"]

@pytest.fixture
def create_user(test_client):
    nums = random.randint(1000,9999)
    email = f"test_{uuid.uuid4()}@test.com"
    obj = {
        "name": f"test{nums}",
        "email": email,
        "password": "12345678",
        "role": "user"
    }

    request = test_client.post('/auth/register', json = obj)
    print(request.text)
    return request.json()["id"]

@pytest.fixture
def create_admin_user(test_client):
    email = f"test_{uuid.uuid4()}@test.com"
    obj = {
        "name": "test",
        "email": email,
        "password": "12345678",
        "role": "admin"
    }

    request = test_client.post('/auth/register', json = obj)
    print(request.text)
    assert request.status_code == 201
    return request.json()["id"]

@pytest.fixture(autouse=True)
def mock_get_current_user(create_user):

    def _mock():
        return {
            "id": create_user,
            "username": "test@test.com"
        }

    app.dependency_overrides[get_current_user] = _mock

    yield

    app.dependency_overrides.clear()

# @pytest.fixture
# def refresh_token(test_client):
#     email = f"test_{uuid.uuid4()}@test.com"
#     user = {
#         "name": "test",
#         "email": email,
#         "password": "12345678",
#         "role": "user"
#     }
#     register = test_client.post("/auth/register",json=user)
#     assert register.status_code == 201

#     payload = {"username": user["email"],"password": "12345678"}
#     response = test_client.post("/auth/token",data=payload)

#     assert response.status_code == 200
#     return response.json()["refresh_token"]