import pytest
from fastapi.testclient import TestClient
import json
from core.main import app

class TestDrinkAPI:
    
    @pytest.mark.asyncio
    async def test_get_drinks(self, test_client):
        response = test_client.get("/drinks")
        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ["page", "name", "desc", "alcoholic", "price", "factory_id"],
                            [
                            (None, None, None, True, None, None),
                            (0,"cwcme", None, False, None, None),
                            (1,2,3,4,5,6),
                            ],)
    
    async def test_get_drinks_with_params(self, test_client, page, name, desc, alcoholic, price, factory_id):
        response = test_client.get("/drinks", 
        params={"page":page, 
                "name":name, 
                "desc":desc, 
                "alcoholic":alcoholic, 
                "price":price,
                "factory_id":factory_id})
        
        assert response.status_code == 200

    @pytest.mark.parametrize("page", [1, 0])
    def test_get_drinks_pagination(self, page, test_client):
        response = test_client.get("/drinks", params={"page":page})
        assert response.status_code == 200


    @pytest.mark.asyncio
    async def test_set_drinks(self, test_client):
        obj = {
        "name": "test",
        "desc": "none",
        "alcoholic": False,
        "price": 111,
        "factory_id": 1,
        }

        response = test_client.post("/drinks", json=obj)

        assert response.status_code == 201

    @pytest.mark.asyncio
    @pytest.mark.parametrize("drink_id, payload",
        [
        (6, {"name":None, "desc": None,}), 
        (8, {"name":None})
        ])
    
    async def test_patch_drinks(self, test_client: TestClient, drink_id: int, payload):
        response = test_client.patch(f"/{drink_id}", params=payload)
        
        assert response.status_code != 400

    @pytest.mark.asyncio
    @pytest.mark.parametrize("drink_id", [0])
    async def test_delete_drinks(self, drink_id, test_client):

        response = test_client.delete(f"/{drink_id}")
        assert response.status_code == 200



class TestOrderService:
    ...