import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

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



class TestFactoriesAPI:
    @pytest.mark.asyncio
    async def test_get_factories(self, test_client):
        response = test_client.get("/factories")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_set_factory(self, test_client):
        obj = {
                "name": "test",
                "location": "test_location"
                }
        
        response = test_client.post("/factories", json=obj)
        assert response.status_code == 201

    @pytest.mark.asyncio
    @pytest.mark.parametrize("factory_id, payload",
            [
            (2, {"name":None, "location": "Moscow",}), 
            (1, {"name":"zavod"})
            ])
        
    async def test_patch_factory(self, test_client: TestClient, factory_id: int, payload):
        response = test_client.patch(f"/factories/{factory_id}", params=payload)
        assert response.status_code != 400
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("factory_id", [2])
    async def test_delete_factory(self, factory_id, test_client):
    
        response = test_client.delete(f"/factories/{factory_id}")
        assert response.status_code == 200

# добавить в сет метод проверку на уже существующий дринк айди 
class TestStocksAPI:
    @pytest.mark.asyncio
    async def test_get_stocks(self, test_client):
        response = test_client.get("/stocks")
        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.parametrize("drink_id, warehouse_id, quantity, reserved_quantity", [(17,1,2,1)])
    async def test_set_stock(self, test_client, drink_id, warehouse_id, quantity, reserved_quantity):
        obj = {
            "drink_id": drink_id,
            "warehouse_id": warehouse_id,
            "quantity": quantity,
            "reserved_quantity": reserved_quantity
        }

        response = test_client.post("/stocks", json=obj)
        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.parametrize("stock_id, quantity, reserved_quantity", [(7, 0, 0)])
    async def test_patch_stock(self, test_client, stock_id, quantity, reserved_quantity):
        obj = {
            "quantity": quantity, 
            "reserved_quantity": reserved_quantity
        }
        response = test_client.patch(f"/stocks/{stock_id}", json = obj)
        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.parametrize("stock_id", [17])
    async def test_delete_stock(self, test_client, stock_id):
        response = test_client.delete(f"/stocks/{stock_id}")
        assert response.status_code == 200

class TestWarehouseAPI:
    @pytest.mark.asyncio
    async def test_get_warehouses(self, test_client):
        response = test_client.get("/warehouses")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_set_warehouse(self, test_client):
        obj = {
                "name": "test",
                "address": "test_location"
            }
            
        response = test_client.post("/warehouses", json=obj)
        assert response.status_code == 201
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("warehouse_id, payload",
            [
            (2, {"name":"склад 22", "location": "Moscow"}), 
            ])
            
    async def test_patch_warehouse(self, test_client: TestClient, warehouse_id: int, payload):
        response = test_client.patch(f"/warehouses/{warehouse_id}", params=payload)
        assert response.status_code != 400
        
    @pytest.mark.asyncio
    @pytest.mark.parametrize("warehouse_id", [3])
    async def test_delete_warehouse(self, warehouse_id, test_client):
        
        response = test_client.delete(f"/warehouses/{warehouse_id}")
        assert response.status_code == 200
