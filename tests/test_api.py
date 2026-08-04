import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from core.auth.router import get_current_user
from core.main import app
import json
from fastapi import Depends
from sqlalchemy.exc import IntegrityError


def mock_get_current_user():
    return {"username": "manager", "id": 8}

app.dependency_overrides[get_current_user] = mock_get_current_user


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
        response = test_client.patch(f"/orders/{order_id}/payment", data ={'username': 'manager', 'id': 8})
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

    # @pytest.mark.asyncio
    # @pytest.mark.parametrize()
    # async def test_add_item_to_order():
    #     ...

    # @pytest.mark.asyncio
    # @pytest.mark.parametrize()
    # async def test_change_item_quantity():
    #     ...

    @pytest.mark.asyncio
    @pytest.mark.parametrize("item_id", [10])
    async def test_delete_warehouse(self, item_id, test_client):
            
        response = test_client.delete(f"/orders/order_items/{item_id}")
        assert response.status_code == 200
    
class TestAuthAPI:
    ...