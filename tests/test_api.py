import pytest
from httpx import AsyncClient, ASGITransport
from core.main import app


# @pytest.mark.asyncio
# async def test_get_drinks():
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
#         response = await ac.get("/drinks")
#         data = response.json()
#         assert data != []

@pytest.mark.asyncio
async def test_set_drinks():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/drinks", json={
            "name": "test",
            "desc": "none",
            "alcoholic": False,
            "price": 111,
            "factory_id": 1
        })
        assert response.status_code == 201