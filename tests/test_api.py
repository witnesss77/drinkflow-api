import pytest
from fastapi.testclient import TestClient
from core.main import app

class TestDrinkAPI:
    
    @pytest.mark.asyncio
    async def test_get_drinks(self, test_client):
        response = test_client.get("/drinks")
        assert response != []

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
        
        assert response != []

    @pytest.mark.parametrize("page", [1, 0, -4])
    def test_get_drinks_pagination(self, page, test_client):
        response = test_client.get("/drinks", params={"page":page})
        assert response.status_code != 409


    @pytest.mark.asyncio
    async def test_set_drinks(self, test_client):
        response = test_client.post("/drinks", 
        params=
        {"name": "test",
        "desc": "none",
        "alcoholic": False,
        "price": 111,
        "factory_id": 1})
        assert response.status_code == 201 

    @pytest.mark.asyncio
    @pytest.mark.parametrize(["drink_id", "page", "name", "desc", "alcoholic", "price", "factory_id"],
                                [
                                (1, None, None, None, True, None, None),
                                (1, 0,"cwcme", None, False, None, None),
                                (1,1,2,3,4,5,6),
                                ],)
    async def test_patch_drinks(self, drink_id: int, test_client, page, name, desc, alcoholic, price, factory_id):
        response = test_client.patch("/drinks/{drink_id}", params={"page":page, 
                        "name":name, 
                        "desc":desc, 
                        "alcoholic":alcoholic, 
                        "price":price,
                        "factory_id":factory_id})
        assert response.status_code != 400

    @pytest.mark.asyncio
    @pytest.mark.parametrize("drink_id", [6])
    async def test_delete_drinks(self, drink_id, test_client):
        response = test_client.delete(f"/drinks/{drink_id}")
        assert response.status_code == 200
   