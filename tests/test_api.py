import pytest
from fastapi.testclient import TestClient
from core.auth.router import get_current_user
from core.main import app
import json




def mock_get_current_user():
    return {"username": "manager", "id": 8}

app.dependency_overrides[get_current_user] = mock_get_current_user


class TestDrinkAPI:
    def test_get_drinks(self, test_client):
        response = test_client.get("/drinks")
        print(response.text)
        assert response.status_code == 200


    @pytest.mark.parametrize("page", [1, 0])
    def test_get_drinks_pagination(self, page, test_client):
        response = test_client.get("/drinks", params={"page":page})
        print(response.text)
        assert response.status_code == 200


    def test_set_drinks(self, test_client):
        obj = {
        "name": "test",
        "desc": "none",
        "alcoholic": True,
        "price": 111,
        "factory_id": 1,
        }

        response = test_client.post("/drinks", json=obj)
        print(response.text)
        assert response.status_code == 201


    @pytest.mark.parametrize(
        ["page", "name", "desc", "alcoholic", "price", "factory_id"],
        [
            (None, None, None, True, None, None),
        ],)
        
    def test_get_drinks_with_params(self, test_client, page, name, desc, alcoholic, price, factory_id):
        params={
        "page":page, 
        "name":name, 
        "desc":desc, 
        "alcoholic":alcoholic, 
        "price":price,
        "factory_id":factory_id}
        
        fix = {k:v for k,v in params.items() if v != None}

        response = test_client.get("/drinks", params = fix)
        print(response.text)
        assert response.status_code == 200


    def test_patch_drinks(self, test_client: TestClient):
        obj = {
        "name": "test",
        "desc": "none",
        "alcoholic": True,
        "price": 111,
        "factory_id": 1,
        }

        response = test_client.post("/drinks", json=obj)
        print(response.text)
        drink_id = response.json()["id"]
        
        response = test_client.patch(f"/drinks/{drink_id}", json = {"name": "test"})
        print(response.text)
        assert response.status_code == 200


    def test_delete_drinks(self, test_client):
        obj = {
                "name": "test",
                "desc": "none",
                "alcoholic": True,
                "price": 111,
                "factory_id": 1,
                }

        response = test_client.post("/drinks", json=obj)
        drink_id = response.json()["id"]
        response = test_client.delete(f"/drinks/{drink_id}")

        print(response.text)
        assert response.status_code == 200


class TestFactoriesAPI:
    def test_get_factories(self, test_client):
        response = test_client.get("/factories")
        print(response.text)
        print(response.text)
        assert response.status_code == 200

    def test_set_factory(self, test_client):
        obj = {
                "name": "test",
                "location": "test_location"
                }

        response = test_client.post("/factories", json=obj)
        print(response.text)
        print(response.text)
        assert response.status_code == 201


    def test_patch_factory(self, test_client: TestClient):
        obj = {
            "name": "zavod",
            "location": "ekodqkodq"
        }

        response = test_client.post("/factories", json=obj)
        print(response.text)
        factory_id = response.json()["id"]

        response = test_client.patch(f"/factories/{factory_id}", json = {"name": "test"})
        print(response.text)
        assert response.status_code == 200


    def test_delete_factory(self, test_client):
        obj = {"name": "test", "location": "test_location"}

        response = test_client.post("/factories", json=obj)
        factory_id = response.json()["id"]

        response = test_client.delete(f"/factories/{factory_id}")
        print(response.text)
        print(response.text)
        assert response.status_code == 200


class TestStocksAPI:
    def test_get_stocks(self, test_client):
        response = test_client.get("/stocks")
        assert response.status_code == 200

    def test_set_stock(self, test_client):
        obj = {
            "drink_id": 1,
            "warehouse_id": 1,
            "quantity": 10,
            "reserved_quantity": 1
        }

        response = test_client.post("/stocks", json=obj)
        print(response.text)
        assert response.status_code == 200
        stock_id = response.json()["id"]

    def test_patch_stock(self, test_client):
        obj = {
        "drink_id": 6,
        "warehouse_id": 1,
        "quantity": 1,
        "reserved_quantity": 11
        }
        
        response = test_client.post("/stocks", json=obj)
        stock_id = response.json()["id"]
        response = test_client.patch(f"/stocks/{stock_id}", json = {"quantity": 32})
        print(response.text)
        assert response.status_code == 200


    def test_delete_stock(self, test_client):
        obj = {
        "drink_id": 7,
        "warehouse_id": 1,
        "quantity": 1,
        "reserved_quantity": 11
        }
                
        response = test_client.post("/stocks", json=obj)
        stock_id = response.json()["id"]
        response = test_client.delete(f"/stocks/{stock_id}")
        print(response.text)
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

class TestOrdersAPI:
    @pytest.mark.asyncio
    async def test_get_orders(self, test_client: TestClient):
        response = test_client.get("/orders")
        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.parametrize(["page", "user_id", "warehouse_id", "status", "is_paid"],
            [(None, None, None, None, False),
            (0, 2, 2, None, None),
            ])
    async def test_get_orders_with_params(self,
        test_client, 
        page, 
        user_id, 
        warehouse_id, 
        status, 
        is_paid):

        obj = {
        "page":page, 
        "user_id":user_id, 
        "warehouse_id":warehouse_id, 
        "status":status, 
        "is_paid":is_paid
        }

        obj = json.dumps(obj)
        response = test_client.get("/orders", 
        params=obj)
        print(response.status_code)
        print(response.text)
        assert response.status_code == 200
    
    @pytest.mark.parametrize("page", [1, 0])
    def test_get_orders_pagination(self, page, test_client: TestClient):
        response = test_client.get("/orders", params={"page":page})
        assert response.status_code == 200

    
    def test_set_order(self, test_client):
        obj = {"user_id": 2, "warehouse_id": 2}
        
        response = test_client.post("/orders", json = obj)
        print(response.text)
        assert response.status_code == 201
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("order_id, payload",
                            
                            [(8, {"status": "in test", "is_paid": False}),]
                            )
    async def test_change_order_status(self, test_client: TestClient, order_id, payload):
        response = test_client.patch(f"/orders/{order_id}/change_status", json=payload)
        print(response.text)
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("order_id", [8])
    async def test_order_payment(self, test_client: TestClient, order_id):
        response = test_client.patch(f"/orders/{order_id}/payment", data = {'username': 'manager', 'id': 8})
        print(response.status_code)
        print(response.text)
        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.parametrize("order_id", [5])
    async def test_delete_order(self, test_client: TestClient, order_id):
        response = test_client.delete(f"/orders/{order_id}")
        assert response.status_code == 200


    @pytest.mark.asyncio
    async def test_get_order_items(self, test_client: TestClient):
        response = test_client.get("/orders/order_items")
        assert response.status_code == 200


    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "order_id, user_id, drink_id, quantity, pricier",
        [
            (6,None,None,None,1),
            (6,None,None,None,None)
        ]
    )
        
        
    async def test_get_order_items_with_params(self, test_client, order_id, user_id, drink_id, quantity, pricier):
        query = {"order_id":order_id, 
                    "user":user_id, 
                    "drink_id":drink_id, 
                    "quantity":quantity, 
                    "pricier":pricier}

        fixed = {k:v for k,v in query.items() if v != None}
        response = test_client.get("/orders/order_items", params = fixed)
        print(response.text)
        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "warehouse_id, payload",
        [
            (2, {"order_id": 5,"user_id": 2,"drink_id": 4,"quantity": 1,"price_per_item": 10})
        ])
    async def test_add_item_to_order(self, test_client, warehouse_id, payload):
        response = test_client.post(f"/orders/order_items/", params = {"warehouse_id": warehouse_id}, json = payload)
        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.parametrize("item_id, payload", 
            [
                (9, {"quantity": 1, "price_per_item": 100})
            ])
    async def test_change_item_quantity(self, test_client: TestClient, item_id, payload):
        response = test_client.patch(f"/orders/order_items/{item_id}", json=payload)
        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.parametrize("item_id", [10])
    async def test_delete_order_item(self, item_id, test_client):
            
        response = test_client.delete(f"/orders/order_items/{item_id}")
        assert response.status_code == 200
    
class TestAuthAPI:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload", 
        [
            ({
                "name": "string",
                "email": "user@example22.com",
                "password": "stringst",
                "role": "admin"
            })
        ])
    async def test_register(self, test_client, payload):
        response = test_client.post('/auth/register', json = payload)
        assert response.status_code == 201


    @pytest.mark.asyncio
    async def test_get_protected_route(self, test_client):
        response = test_client.get("/auth/me")
        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload", 
        [
            ({"username": "str", "password": 12345678}),
        ])
    async def test_get_access_token(self, test_client, payload):
        response = test_client.post('/auth/token', data = payload)
        print(response.text)
        test_token = response.json()["refresh_token"]
        print(test_token)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_refresh_access_token(self, test_client, refresh_token: str):
        response = test_client.post("/auth/refresh", params={"refresh_token": refresh_token})
        print(response.text)
        assert response.status_code == 200